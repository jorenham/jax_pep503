# PEP 503 repository index for `jax[cuda]`

*Daily automatically rebuilds*

## Repository

https://jorenham.github.io/jax_pep503/

## Example: Adding `jax[cuda]` to your [Poetry](https://python-poetry.org/) project

- Add the repository as a secondary source to your `pyproject.toml`:

    ```toml
    ...
    
    [[tool.poetry.source]]
    name = "jorenham/jax_pep503"
    url = "https://jorenham.github.io/jax_pep503/"
    secondary = true
    
    ...
    ```

- Now you can add `jax[cuda]` using:

    ```bash
    poetry add jax[cuda]
    ```

See the [example project](example_project) for more details 
