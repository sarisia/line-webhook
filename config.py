from pathlib import Path
import json
import string
import random


class Config():
    def __init__(self, rundir, file='config.json'):
        self._file = Path(rundir).parent/'config'/file
        self._config = {}

        self._init_config(file)
    
    @property
    def is_ready(self):
        return bool(self._config)
    
    def get(self, name):
        return self._config.get(name)

    def _init_config(self, file):
        if not self._file.exists():
            print(f'{str(self._file)} not found.')
            return

        with open(self._file, 'r', encoding='utf8') as f:
            try:
                self._config = json.load(f)
            except:
                print(f'Failed to parse {file}.')

class Unique(Config):
    def __init__(self, rundir):
        super().__init__(rundir, file='unique.json')

    def _deserialize(self):
        with open(self._file, 'w', encoding='utf8') as f:
            json.dump(self._config, f)

    def register(self, id):
        rand = ''.join([random.choice(string.ascii_lowercase + string.digits) for i in range(20)])
        self._config[rand] = id
        self._deserialize()
        return rand
