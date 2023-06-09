import collections
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Final, TypeAlias

import aioboto3
import botocore
import botocore.config
import yarl
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates


ENDPOINT: Final[str] = 'https://storage.googleapis.com'
BUCKET: Final[str] = 'jax-releases'
JAX_URL: Final[yarl.URL] = yarl.URL(ENDPOINT) / BUCKET

RELEASE_SUFFIXES: Final = frozenset({'.whl', '.gz'})
RESCRAPE_INTERVAL: Final[timedelta] = timedelta(days=1)


app: Final = FastAPI()
templates: Final = Jinja2Templates(directory='templates')


_HTMLAttrs: TypeAlias = dict[str, str]
_Links: TypeAlias = dict[str, _HTMLAttrs]


_last_scrape = datetime.min
_package_links = None


async def get_package_links() -> _Links:
    return {
        package_name: {'href': f'{package_name}/'}
        for package_name in (await get_links())
    }


async def get_package_release_links(package_name: str) -> _Links:
    return (await get_links())[package_name]


async def get_links() -> dict[str, _Links]:
    global _last_scrape, _package_links

    if not _package_links or datetime.now() - _last_scrape > RESCRAPE_INTERVAL:
        _package_links = await _get_links()
        _last_scrape = datetime.now()

    return _package_links


async def _get_links() -> dict[str, _Links]:
    links = collections.defaultdict(dict)

    session = aioboto3.Session()
    config = botocore.config.Config(signature_version=botocore.UNSIGNED)
    async with session.resource(
        's3',
        endpoint_url=ENDPOINT,
        config=config
    ) as s3:
        bucket = await s3.Bucket(BUCKET)
        async for release_data in bucket.objects.all():
            if not await release_data.size:
                continue

            release = urllib.parse.unquote(release_data.key)
            ext = Path(release).suffix
            if not ext or ext in ('.html', '.so'):
                continue

            url = JAX_URL / release
            if not (name := url.name):
                continue

            package_name, tag, *tail = name.split('-')
            attrs = {'href': str(url)}

            if tail:
                version_raw = tail[0]
                assert version_raw.startswith('cp'), (release, version_raw)

                version = int(version_raw[2]), int(version_raw[3:])
                version_str = '.'.join(map(str, version))

                attrs['data-requires-python'] = version_str

            links[package_name][release] = attrs

    return links


def render_listing(request: Request, title: str, links: _Links, **context):
    context = {'request': request, 'title': title, 'links': links} | context
    return templates.TemplateResponse('listing.html', context)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    links = await get_package_links()

    return render_listing(request, title='Simple index', links=links)


@app.get('/{name}/', response_class=HTMLResponse)
async def package(request: Request, name: str):
    title = f'Links for {name}'
    links = await get_package_release_links(name)

    return render_listing(request, title=title, heading=title, links=links)
