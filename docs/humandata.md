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

- 'date': Date of HumanData creation

- 'slice_number': Number of slices of HumanData, if a dataset is very large and needs to be split into smaller parts. If not applicable, set to `1`.

- 'slice_id': Slice id of HumanData file.

- 'version': Version of HumanData, see version changes in [Change Log](/converter/supported_dataset.md#version-changes).


## Configurations - `HumanData['config']`

Defines the annotations included in this HumanData, keys include, if any key is not applicable, set to `None`:

- 'path': list, recording what path is included, should be a sublist of ['image', 'depth', 'pointcloud', etc.] 

- 'model': string, should be one of ['smpl', 'smplx']

- 'keypoint': list, recording what keypoints are included, should be a sublist of ['2d', '3d', '2d_smplx', '3d_smplx', '2d_smpl', '3d_smpl'], each element have its corresponding mask.

- 'bbox': list, recording what bounding box is included, should be a sublist of ['body', 'head', 'left_hand', 'right_hand']

- 'camera': list, recording what camera information is included, should be a sublist of ['intrinsics', 'extrinsics']

- 'temporal': list, recording what temporal information is included, should be a sublist of ['frame_id', 'track_id', 'camera_view', 'sequence_name']

- 'specific': list, recording what dataset-specific information is included, should be a list.

## Data Paths - `HumanData['path']`

Align with `HumanData['config']['path']`, for example

- 'image': list of image path, real image path should be
    ```
    os.path.join('<your dataset base dir>', HumanData['metadata']['dataset'], HumanData['path']['image'][0])
    ```

## Human Pose and Shape - `HumanData['smpl']/['smplx']`

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

## Keypoint Annotations - `HumanData['keypoint']`

Depending on the dataset, can include several keypoints, where K is the number of keypoints, and the last element of 3d keypoints is the confidence score.

- '2d': (N, K, 3)
- '2d_convention': string, the name of keypoints convention
- '3d': (N, K, 4)
- '3d_convention': string, the name of keypoints convention
- '2d_smpl': (N, 45, 3)
- '3d_smpl': (N, 45, 4)
- '2d_smplx': (N, 144, 3)
- '3d_smplx': (N, 144, 4)

## Bounding Box - `HumanData['bbox']`

All bounding box should be in format of (N, 5), with the first 4 elements as **[x1, y1, w, h]**, and the last element as the confidence score.

- 'body'
- 'head'
- 'left_hand'
- 'right_hand'

## Camera Information - `HumanData['camera']`

Camera follows opencv format, with the following keys:

- 'intrinsics': (N, 3, 3)
- 'extrinsics': (N, 4, 4)

## Temporal Information - `HumanData['temporal']`

Track id will be same across different camera views.

- 'frame_id': (N, 1)
- 'track_id': (N, 1)
- 'camera_view': (N, 1)
- 'sequence_name': (N, 1)

## Dataset Specific Information - `HumanData['specific']`

Keys align with `HumanData['config']['specific']`, each key is a string (0-1 mask), with keys align with the corresponding config.


## (Contact) - to be updated