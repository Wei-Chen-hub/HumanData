# HumanData Format

HumanData is a subclass of python built-in class dict, with several small **dicts** as its keys. It is designed to support Multi-Human, Temporal data in Camera Space.

```
HumanData = dict(np.load('path/to/humandata.npz', allow_pickle=True))
```
OR (to be implemented)
```
From ... import HumanData
HumanData = HumanData.from_npz('path/to/humandata.npz')
```

## MetaData - `HumanData['metadata']`

Keys include:

- 'dataset': Name of dataset, string, see [supported list](/converter/supported_dataset.md).

- 'subset': Name of subset, string, including `['train', 'val', 'test']` and other dataset-specific subsets.

- 'datatype': 要加这个吗

- 'date': Date of HumanData creation

- 'slice': Slice id of HumanData, if a dataset is very large and needs to be split into smaller parts. If not applicable, set to `-1`.

- 'version': Version of HumanData, see version changes in [Change Log](/converter/supported_dataset.md#version-changes).


## Configurations - `HumanData['config']`

Defines the annotations included in this HumanData, keys include, if any key is not applicable, set to `None`:

- 'path': list, recording what path is included, should be a sublist of ['image', 'depth', 'pointcloud', etc.] 

- 'model': string, should be one of ['smpl', 'smplx']

- 'keypoint': list, recording what keypoints are included, should be a sublist of ['2d', '3d', '2d_smplx', '3d_smplx', '2d_smpl', '3d_smpl'], each element have its corresponding mask.

- 'bbox': list, recording what bounding box is included, should be a sublist of ['body', 'head', 'left_hand', 'right_hand']

- 'camera': list, recording what camera information is included, should be a sublist of ['intrinsics', 'extrinsics']

- 'temporal': list, recording what temporal information is included, should be a sublist of ['frame_id', 'track_id', 'camera_view', 'sequence_name']

## Data Paths

## Smpl / Smplx Parameters

## Keypoint Annotations

## Bounding Box

## Camera Information

## Temporal Information

## (Contact) - to be updated