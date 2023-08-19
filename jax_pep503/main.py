import collections
import re
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final, TypeAlias

import aioboto3
import botocore
import botocore.config
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates


ENDPOINT: Final[str] = 'https://storage.googleapis.com'
BUCKET: Final[str] = 'jax-releases'
JAX_URL: Final[str] = f'{ENDPOINT}/{BUCKET}'

RELEASE_SUFFIXES: Final[frozenset[str]] = frozenset({'.whl', '.gz'})
RESCRAPE_INTERVAL: Final[timedelta] = timedelta(days=1)

# https://peps.python.org/pep-0491/#file-format
WHEEL_FILE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r'(?P<distribution>\w+)'
    r'-(?P<version>.+)'
    r'(?:-(?P<build>\w+))?'
    r'-(?P<lang_tag>'
    r'(?P<lang_impl>[a-z]+)'
    r'(?P<lang_version_major>[234])'
    r'(?P<lang_version_minor>\d{,2})'
    r')'
    r'-(?P<abi_tag>\w+)'
    r'-(?P<platform_tag>\w+)'
)


app: Final[FastAPI] = FastAPI()
templates: Final[Jinja2Templates] = Jinja2Templates(directory='templates')


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
    links: dict[str, _Links] = collections.defaultdict(dict)

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
            release_path = Path(release)

            release_ext = release_path.suffix
            if not release_ext or release_ext in {'.html', '.so'}:
                continue

            if not (name := release_path.stem):
                continue

            if not (match := WHEEL_FILE_PATTERN.match(name)):
                continue

            groups = match.groupdict()
            
            py_version = groups['lang_version_major']
            if py_version_minor := groups['lang_version_minor']:
                py_version = f'{py_version}.{py_version_minor}'

            links[groups['distribution']][release] = {
                'href': f'{JAX_URL}/{release}',
                'data-requires-python': py_version,
                'data-gpg-sig': 'false',
            }

    return links


def render_listing(
    request: Request,
    title: str,
    links: _Links, 
    **context: Any,
) -> Response:
    return templates.TemplateResponse(  # type: ignore
        'listing.html', 
        {'request': request, 'title': title, 'links': links} | context,
    )


@app.get('/', response_class=HTMLResponse)
async def index(request: Request) -> Response:
    return render_listing(
        request,
        title='Simple index', 
        links=await get_package_links(),
    )


@app.get('/{name}/', response_class=HTMLResponse)
async def package(request: Request, name: str) -> Response:
    title = f'Links for {name}'

    return render_listing(
        request, 
        title=title,
        heading=title, 
        links=await get_package_release_links(name),
    )
