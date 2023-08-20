# Example Poetry project with `jax[cuda]`

 - Install with `poetry install`

 - To verify correct installation, run: `poetry run devices`. 
 You should see an output similar to:
  ```
  default_backend: gpu 
  
  devices:
          device_kind  : NVIDIA GeForce RTX 4060 Laptop GPU
          device_vendor: NVIDIA Corporation
          platform     : gpu
  ```
