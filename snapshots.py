from pathlib import Path
from xml.etree import ElementTree


_type_symbol = {
    'single': '-',
    'pre': '┌',
    'post': '└',
}

_cleanup_symbol = {
    '': ' ',
    'number': 'n',
    'timeline': 't',
}


class Snapshot:
    def __init__(self, dir: Path):
        self.dir = dir
        try:
            self.num = int(dir.name)
        except ValueError:
            self.num = -1
        self.subvol = dir / 'snapshot'
        info_file = dir / 'info.xml'
        self.is_valid = self.subvol.is_dir() and info_file.is_file() and self.num >= 0
        if self.is_valid:
            try:
                info = ElementTree.parse(info_file).getroot()
                self.type = info.find('type').text
                self.date = info.find('date').text
                description = info.find('description')
                self.description = description.text if description is not None else ''
                cleanup = info.find('cleanup')
                self.cleanup = cleanup.text if cleanup is not None else ''
                if info.find('num').text != dir.name:
                    self.is_valid = False
            except:
                self.is_valid = False
    
    def __repr__(self) -> str:
        return f'{self.num:>5} {_type_symbol[self.type]} {self.date}  {_cleanup_symbol[self.cleanup]}  {self.description}'


class System:
    def __init__(self, dir: Path):
        self.dir = dir
        self.name = dir.name
        self.main_subvol = dir / '@'
        self.snapshot_subvol = dir / '@.snapshots'
        self.is_valid = self.main_subvol.is_dir() and self.snapshot_subvol.is_dir()
    
    def __repr__(self) -> str:
        return self.name
    
    def get_snapshots(self) -> list[Snapshot]:
        snapshots = (
            Snapshot(d)
            for d in self.snapshot_subvol.iterdir()
            if d.is_dir()
        )
        valid_snapshots = (s for s in snapshots if s.is_valid)
        return sorted(valid_snapshots, key=lambda s: s.num)


def get_systems(config: dict) -> list[System]:
    root_path = Path(config['root'])
    exclude = set(config['exclude'])
    
    systems = (
        System(d)
        for d in root_path.iterdir()
        if d.is_dir() and d.name not in exclude
    )
    valid_systems = (s for s in systems if s.is_valid)
    return sorted(valid_systems, key=lambda s: s.name)
