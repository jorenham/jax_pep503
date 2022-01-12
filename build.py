import pathlib

from fastapi.testclient import TestClient

from main import app

HTML_DIR = pathlib.Path('./docs')
URL_PATHS = '/', '/jaxlib/'


client = TestClient(app)


def build_index(html_dir: pathlib.Path):
    html_dir.mkdir(exist_ok=True)

    for url_path in URL_PATHS:
        response = client.get(url_path)
        response.raise_for_status()

        html_path = html_dir / url_path.removeprefix('/')
        if not url_path.endswith('.html'):
            html_path.mkdir(parents=True, exist_ok=True)
            html_path /= 'index.html'

        print(f'{url_path} -> {html_path}')
        html_path.write_bytes(response.content)


if __name__ == '__main__':
    build_index(HTML_DIR)
