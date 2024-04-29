# HumanData Format

HumanData is a subclass of python built-in class dict, with several small dicts as its keys. It is designed to support Multi-Human, Temporal data in Camera Space.

```
HumanData = dict(np.load('path/to/humandata.npz', allow_pickle=True))
```
OR (to be implemented)
```
From ... import HumanData
HumanData = HumanData.from_npz('path/to/humandata.npz')
```

## Configuration

Configuration info are stored in `HumanData['config']` as a dict. Keys include:

- 'dataset': Name of dataset, see [supported list](/converter/supported_dataset.md).







  


## Data Paths

## Smpl / Smplx Parameters

## Keypoint Annotations

## Bounding Box

## Camera Information

## Temporal Information

## (Contact) - to be updated