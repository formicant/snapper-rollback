# snapper-rollback

My personal python script for rolling back [Snapper](http://snapper.io) snapshots.


## BTRFS subvolume structure

I have multiple Linux distros installed inside a single BTRFS volume.

Each OS has its own directory in the volume root with multiple subvolumes inside:
- `@` — main subvolume mounted as `/` that is snapshotted by Snapper
- `@var_tmp`, `@var_log`, `@var_cache` etc — miscellaneous subvolumes that are not snapshotted
- `@.snapshots` — subvolume with Snapper snapshots

The whole volume directory tree looks like this:
```
BTRFS root
├ ‘arch’ (directory)
│  ├ ‘@’ (subvolume)
│  ├ ... (subvolumes)
│  └ ‘@.snapshots’ (subvolume)
│     ├ ‘1’ (directory)
│     │  ├ ‘info.xml’ (file)
│     │  └ ‘snapshot’ (subvolume)
│     ├ ‘2’ (directory)
│     │  ├ ‘info.xml’ (file)
│     │  └ ‘snapshot’ (subvolume)
│     └ ... (directories)
├ ‘debian’ (directory)
│  ├ ‘@’ (subvolume)
│  ├ ... (subvolumes)
│  └ ‘@.snapshots’ (subvolume)
│     ├ ‘1’ (directory)
│     │  ├ ‘info.xml’ (file)
│     │  └ ‘snapshot’ (subvolume)
│     └ ... (directories)
└ ... (directories)
```

The script implies this exact structure.


## Configuration

The `config.toml` file contains the script parameters:
- `root` — path where the BTRFS root is mounted. E.g. `/mnt/btrfs-root`
- `exclude` — list of directory names in the BTRFS root to exclude
  
  (directories without `@` and `@.snapshots` inside are excluded automatically)


## Running the script

The script has no dependencies. Tested on Python 3.11 and 3.12.
Should also work with some earlier Python versions.

Must be executed with `sudo` from the directory with `config.toml`:
```bash
sudo python3 snapper-rollback
```


## Script UI

Navigation:
- <kbd>↑</kbd>, <kbd>↓</kbd>, <kbd>PgUp</kbd>, <kbd>PgDn</kbd>, <kbd>Home</kbd>, <kbd>End</kbd> — move cursor
- <kbd>Enter</kbd>, <kbd>Space</kbd> — select
- <kbd>Esc</kbd>, <kbd>BackSpace</kbd> — go back

First, the script asks to choose an operating system:
```
Select operating system:

[arch]
 debian
 mint
```

Then, a snapshot
(pre-post pairs are shown connected by a bracket):
```
Operating system: arch

Select snapshot to rollback to:

 4462 ╶ 2024-07-23 12:42:43     ok
 4472 ╶ 2024-07-23 16:00:07  t  timeline
 4633 ┌ 2024-08-10 04:03:56  n  pacman -S -y -u --config /etc/pacman.conf --
 4634 └ 2024-08-10 04:04:04  n  bluedevil breeze breeze-gtk breeze5 discover
 4652 ╶ 2024-08-11 17:00:03  t  timeline
 4658 ┌ 2024-08-12 14:26:22  n  pacman -S -u -y --config /etc/pacman.conf --
 4659 └ 2024-08-12 14:27:27  n  aardvark-dns containers-common cracklib
[4674 ╶ 2024-08-14 04:00:28  t  timeline]
```

Then, the commands that will be executed are shown with a confirmation:
```
Operating system: arch
Rollback to snapshot:
 4674 ╶ 2024-08-14 04:00:28  t  timeline

# /usr/bin/btrfs subvolume delete /mnt/btrfs-root/arch/@
# /usr/bin/btrfs subvolume snapshot /mnt/btrfs-
  root/arch/@.snapshots/4674/snapshot /mnt/btrfs-root/arch/@

Are you sure?

[No]
 Yes
```

After the confirmation, the script prints the output of the commands and suggests rebooting:
```
> Delete subvolume 12980 (no-commit): '/mnt/btrfs-root/arch/@'
> Create snapshot of '/mnt/btrfs-root/arch/@.snapshots/4674/snapshot'
  in '/mnt/btrfs-root/arch/@'

Rollback completed

[Reboot]
 Exit
```

In case of error, a python exception with the error message is printed.
