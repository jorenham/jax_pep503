import collections
from datetime import datetime, timedelta
import re
from pathlib import Path
from typing import Final, TypeAlias

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import httpx
import yarl


JAX_URL: Final = yarl.URL('https://storage.googleapis.com/jax-releases/')
PATTERN_XML_KEY: Final = re.compile(r'<Key>(.*?)</Key>')
RESCRAPE_INTERVAL: Final = timedelta(days=1)
RELEASE_SUFFIXES: Final = frozenset({'.whl', '.gz'})


app: Final = FastAPI()
templates: Final = Jinja2Templates(directory='templates')


_HTMLAttrs: TypeAlias = dict[str, str]
_Links: TypeAlias = dict[str, _HTMLAttrs]


_last_scrape = datetime.min
_package_links = None


async def get_package_links() -> _Links:
    links = {}
    for package_name in (await get_links()):
        links[package_name] = {'href': f'{package_name}/'}
    return links


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

    async with httpx.AsyncClient() as client:
        r: httpx.Response = await client.get(str(JAX_URL))
        r.raise_for_status()

        xml = r.text
        for release in re.findall(PATTERN_XML_KEY, xml):
            if Path(release).suffix not in RELEASE_SUFFIXES:
                continue

            url = JAX_URL / release

            if not (name := url.name):
                continue

            package_name, tag, *tail = name.split('-')

            attrs = {'href': str(url)}

            if tail:
                version_raw = tail[0]
                assert version_raw.startswith('cp')

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
