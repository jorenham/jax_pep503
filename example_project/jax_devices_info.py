import jax


def print_devices():

    print('default_backend:', jax.default_backend(), '\n')

    print('devices:')
    for device in jax.devices():
        for attr in ('device_kind', 'device_vendor', 'platform'):
            print(f'\t{attr: <13}:', getattr(device, attr, 'x'))


if __name__ == '__main__':
    print_devices()
