# PEP 503 compliant repository index for Jax(lib)

This makes adding e.g. `jax[cuda]` to your poetry project possible by 
adding this repository in your `pyproject.toml`:

```toml
[[tool.poetry.source]]
name = "jorenham/jax_pep503"
url = "https://jorenham.github.io/jax_pep503/"
secondary = true
```
