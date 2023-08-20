# PEP 503 repository index for `jax[cuda]`

*Daily automatically rebuilds*

## Repository

https://jorenham.github.io/jax_pep503/

## Example: Adding `jax[cuda]` to a [Poetry](https://python-poetry.org/) project

- Add the repository as a secondary source to your `pyproject.toml`:

    ```toml
    ...
    
    [[tool.poetry.source]]
    name = "PyPI"
    priority = "primary"

    [[tool.poetry.source]]
    name = "jorenham/jax_pep503"
    url = "https://jorenham.github.io/jax_pep503/"
    priority = "supplemental"

    [tool.poetry.dependencies]
    ...
    ```

- Now you can add `jax[cuda]` using:

    ```bash
    poetry add jax[cuda]
    ```

See the [example project](example_project) for more details.

## See also

- [PEP 503 – Simple Repository API](https://peps.python.org/pep-0503/)
- [google/jax](https://github.com/google/jax)
- [google/jax#5410 – Please provide PEP 503 compliant indices for CUDA versions of packages](https://github.com/google/jax/issues/5410)
- [jax-releases](https://storage.googleapis.com/jax-releases/) (not compatible with PEP 503)
