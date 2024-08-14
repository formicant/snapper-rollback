from shutil import which
from shlex import quote
from subprocess import Popen, PIPE


class Command:
    def __init__(self, command: str, arguments: list[str]):
        command_path = which(command)
        if command_path is None:
            raise FileNotFoundError(f'Cannot find command {command}')
        self.args = [command_path, *arguments]
    
    def __repr__(self) -> str:
        return ' '.join(quote(a) for a in self.args)
    
    def execute_and_get_output(self) -> str:
        process = Popen(self.args, text=True, stdout=PIPE, stderr=PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            raise SystemError(error)
        return output
    
    def execute_without_waiting(self) -> None:
        Popen(self.args)
