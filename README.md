# psync

A naive tool for syncing partitions using rsync

---

## Arch Linux package available on AUR
[https://aur.archlinux.org/packages/psync/](https://aur.archlinux.org/packages/psync/)


## Hot to use

Create your own `config.yaml` following the `simple_config.yaml` in `examples` directory.

The default location for your config file is `~/.config/psync/config.yaml`

Alternatively, you can use the config option to use a custom location
```
sudo psync --config path_for_your_config
```

To find out the `filesystem UUID`, use
```
lsblk -f
```

Once you finish your config file check if everything is OK, without copying anything, using
```
sudo psync --dry --verbose
```

If everything is right, to copy your files from `source` to `target` use
```
sudo psync
```

If you need/want copy from `target` to `source`, use the reverse option
```
sudo psync --reverse
```

To see all available options use
```
psync --help
```

## Config sections
You can pass any section(s) you want to sync using command line arguments
```
sudo psync arch
sudo psync home arch
sudo psync ntfs arch home
```

If you don't pass anything, all them will be synced.
```
sudo psync
```

## Source and Target

No reverse option:
- `real source` = config source
- `real target` = config target

If you pass the reverse option:
- `real source` = config target
- `real target` = config source

Note that `psync` expects that the `real target` it's not mounted, because it will be mounted in `mount_path` (from config file). Also note that `mount_path` must exist, `psync` will not create it.


## That's all folks!
Enjoy it!

**Pull requests to fix or improve `psync` are welcome.**
