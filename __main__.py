import tomllib
from pathlib import Path
from os import getuid
from snapshots import System, Snapshot, get_systems
from command import Command
from ui import UI


def get_config() -> dict:
    config_path = Path(__file__).parent / 'config.toml'
    with open(config_path, 'rb') as config_file:
        return tomllib.load(config_file)


def reboot() -> None:
    reboot_command = Command('reboot', [])
    reboot_command.execute_without_waiting()


def get_rollback_commands(main_subvol: Path, snapshot_subvol: Path) -> list[Command]:
    return [
        Command('btrfs', [
            'subvolume', 'delete',
            main_subvol.as_posix()
        ]),
        Command('btrfs', [
            'subvolume', 'snapshot',
            snapshot_subvol.as_posix(),
            main_subvol.as_posix()
        ]),
    ]


def show_systems_page(ui: UI, systems: list[System]) -> System|None:
    items = [f'{s}' for s in systems]
    index = ui.show_selection_page(['Select operating system:'], items)
    return systems[index] if index is not None else None


def show_snapshots_page(ui: UI, system: System, snapshots: list[Snapshot]) -> Snapshot|None:
    items = [f'{s}' for s in snapshots]
    index = ui.show_selection_page(
        [
            f'Operating system: {system}',
            '',
            'Select snapshot to rollback to:',
        ],
        items,
        default_index=len(items) - 1
    )
    return snapshots[index] if index is not None else None


def show_confirmation_page(ui: UI, system: System, snapshot: Snapshot, commands: list[Command]) -> bool:
    index = ui.show_selection_page(
        [
            f'Operating system: {system}',
            'Rollback to snapshot:',
            f'{snapshot}',
            '',
            *[f'# {c}' for c in commands],
            '',
            'Are you sure?',
        ],
        ['No', 'Yes']
    )
    return index == 1


def show_reboot_page(ui: UI, text: list[str]) -> bool:
    index = ui.show_selection_page(
        [*text],
        ['Reboot', 'Exit']
    )
    return index == 0


def main(ui: UI) -> None:
    config = get_config()
    systems = get_systems(config)
    
    while True:
        system = show_systems_page(ui, systems)
        if system is None:
            if show_reboot_page(ui, ['Exiting']):
                reboot()
            return
        
        snapshots = system.get_snapshots()
        while True:
            snapshot = show_snapshots_page(ui, system, snapshots)
            if snapshot is None:
                break
            
            rollback_commands = get_rollback_commands(system.main_subvol, snapshot.subvol)
            confirmation = show_confirmation_page(ui, system, snapshot, rollback_commands)
            if not confirmation:
                continue
            
            outputs = [f'> {c.execute_and_get_output()}' for c in rollback_commands]
            if show_reboot_page(ui, [*outputs, '', 'Rollback completed']):
                reboot()
            return


if __name__ == '__main__':
    if getuid() == 0:
        UI('Snapper Rollback', main)
    else:
        print('The script should be executed with sudo')
        exit(-1)
