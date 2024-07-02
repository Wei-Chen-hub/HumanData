import argparse
import os
import time
import importlib

from abc import ABCMeta, abstractmethod

from converter.dataset_configs import DATASET_CONFIGS
from scripts.emdb import EmdbConverter

def parse_args():
    parser = argparse.ArgumentParser(description='Convert datasets')

    parser.add_argument(
        '--root_path',
        type=str,
        required=True,
        help='the root path of original data')

    parser.add_argument(
        '--output_path',
        type=str,
        required=True,
        help='the path to store the preprocessed npz files')

    parser.add_argument(
        '--datasets',
        type=str,
        nargs='+',
        required=True,
        default=[],
        help=f'Supported datasets: {list(DATASET_CONFIGS.keys())}')

    parser.add_argument(
        '--modes',
        type=str,
        nargs='+',
        required=False,
        default=[],
        help='Need to comply with supported modes'
        'specified in tools/convert_datasets.py')

    parser.add_argument(
        '--prefix',
        type=str,
        required=False,
        default=None,
        help='Use this prefix to target a specific dataset')

    args = parser.parse_args()

    return args


def main(args):
    datasets = (
        DATASET_CONFIGS.keys() if args.datasets == ['all'] else args.datasets)

    for dataset in datasets:
        print(f'[{dataset}] Converting ...')
        cfg = DATASET_CONFIGS[dataset]
        
        # modify modes
        if args.modes != []:
            assert all(x in cfg['modes'] for x in args.modes), \
                f'Unsupported mode found, supported mode for ' \
                f'{cfg["prefix"]} is {cfg["modes"]}'
            cfg['modes'] = args.modes
        else:
            print(f'For {cfg["prefix"]}, modes: {cfg["modes"]} are available,'
                  ' process all modes as not specified')
            args.modes = cfg['modes']

        # modify cfg
        cfg['root_path'] = args.root_path
        cfg['out_path'] = args.output_path
        cfg['dataset_path'] = os.path.join(args.root_path, cfg['prefix'])

        # import converter and initialize
        converter = getattr(importlib.import_module(f'converter.scripts.{cfg["prefix"]}'), cfg['type'])
        converter = converter(cfg)
        for mode in args.modes:
            cfg['mode'] = mode
            converter.convert_by_mode(**cfg)

        print(f'[{dataset}] Converting finished!')


if __name__ == '__main__':
    
    args = parse_args()

    main(args)