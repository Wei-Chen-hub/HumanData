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

- 'dataset': Name of dataset, string, see [Supported List](/converter/supported_dataset.md).

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

## Data Paths - `HumanData['path']`

Align with `HumanData['config']['path']`, for example

- 'image': list of image path, real image path should be
    ```
    os.path.join('<your dataset base dir>', HumanData['metadata']['dataset'], HumanData['path']['image'][0])
    ```

## Human Pose and Shape- `HumanData['smpl']/['smplx']`

A dict, which name aligns with config, in one of the following format:

- 'smpl': 
    ```
    HumanData['smpl'] = {
            'body_pose': (N, 69),
            'betas': (N, 10),
            'global_orient': (N, 3),
            'transl': (N, 3)}
    ```
- 'smplx':
    ```
    HumanData['smplx'] = {
            'betas': (N, 10),
            'transl': (N, 3),
            'global_orient': (N, 3),
            'body_pose': (N, 21, 3),
            'left_hand_pose': (N, 15, 3),
            'right_hand_pose': (N, 15, 3),
            'leye_pose'*: (N, 3),
            'reye_pose'*: (N, 3),
            'jaw_pose'*: (N, 3),
            'expression'*: (N, 10)}
    ```

Some dataset with smplx annotations may not have all the keys, possible missing keys are marked with `*`.

Additional keys:

- 'source': should be one of ['']


Some dataset may have additional valid keys, including `['待补充']`, these will be stored in a 0-1 list.

## Keypoint Annotations




## Bounding Box

## Camera Information

## Temporal Information

## (Contact) - to be updated