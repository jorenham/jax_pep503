import asyncio
import pathlib

from fastapi.testclient import TestClient
from mainpy import main

from jax_pep503.main import app, get_package_links

HTML_DIR = pathlib.Path('./docs')


client = TestClient(app)


def build_index():
    asyncio.run(_build_index())


@main
async def _build_index(html_dir: pathlib.Path = HTML_DIR):
    html_dir.mkdir(exist_ok=True)

    url_paths = ['/']

    package_links = await get_package_links()
    url_paths.extend(f'/{package}/' for package in package_links)
    for url_path in url_paths:
        response = client.get(url_path)
        response.raise_for_status()

        html_path = html_dir / url_path.removeprefix('/')
        if not url_path.endswith('.html'):
            html_path.mkdir(parents=True, exist_ok=True)
            html_path /= 'index.html'

        print(f'{url_path} -> {html_path}')
        html_path.write_bytes(response.content)
