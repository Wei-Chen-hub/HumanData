from abc import ABCMeta, abstractmethod

class BaseModeConverter(metaclass=ABCMeta):
    """Base dataset.
    Need to be implemented by each dataset.

    Args:
        prefix (str): the prefix of data path
        modes (list): the modes of data for converter
    """

    ACCEPTED_MODES = None

    def __init__(self, config: dict):
        self.modes = config.get('modes', [''])

        for mode in self.modes:
            if mode not in self.ACCEPTED_MODES:
                raise ValueError(f'Input mode not in {self.ACCEPTED_MODES}')
        # process all modes if not specified
        if len(self.modes) == 0:
            self.modes = self.ACCEPTED_MODES


    def convert(self, dataset_path: str, out_path: str, *args, **kwargs):
        for mode in self.modes:
            self.convert_by_mode(dataset_path, out_path, mode, *args, **kwargs)

    @abstractmethod
    def convert_by_mode(self):
        pass
