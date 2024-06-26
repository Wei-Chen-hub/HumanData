import glob
import os
import pdb
import random
import json
import pickle
import cv2
import smplx

import numpy as np
import torch
from tqdm import tqdm

from converter.utils.base_converter import BaseModeConverter
from converter.utils.human_data import HumanData

class EmdbConverter(BaseModeConverter):

    ACCEPTED_MODES = ['emdb1', 'emdb2', 'else']

    def __init__(self, modes=[]):

        self.device = torch.device(
            'cuda') if torch.cuda.is_available() else torch.device('cpu')
        
        self.misc_config = dict(
            bbox_source='keypoints2d_smpl',
            smpl_source='original',
            cam_param_type='prespective',
            kps3d_root_aligned=False,
            has_gender=True,
        )
        
        self.smpl_shape = {
            'body_pose': (-1, 69),
            'betas': (-1, 10),
            'global_orient': (-1, 3),
            'transl': (-1, 3),} 
        self.smpl_mapping = {
            'betas': 'betas',
            'transl': 'trans',
            'global_orient': 'poses_root',
            'body_pose': 'poses_body',}
        self.smpl_config = {
            'num_betas': 10,
            'use_pca': False,
            'batch_size': 1,}
        
        super(EmdbConverter, self).__init__(modes)


    def convert_by_mode(self, dataset_path: str, out_path: str, mode: str, 
                        human_model_path: str, **kwargs) -> dict:
        print('Converting EMDB dataset...')

        # ----------------metadata----------------

        # prepare metadata
        metadata = {}
        metadata['dataset'] = mode
        metadata['date'] = '20240702'
        metadata['slice_number'] = 1
        metadata['slice_id'] = 1
        metadata['version'] = '1.0'

        # prepare config
        config = {}
        config['model'] = 'smpl'
        config['path'] = ['image']
        config['keypoints'] = ['2d', '3d', '2d_smpl', '3d_smpl']
        config['bbox'] = ['body', 'head', 'left_hand', 'right_hand']
        config['camera'] = ['intrinsics', 'extrinsics']
        config['temporal'] = ['frame_id', 'track_id', 'camera_view', 'sequence_name']

        # ----------------create body model----------------

        # build smpl model
        body_model_gendered = {}
        for gender in ['male', 'female', 'neutral']:
            kwargs = self.smpl_config.copy()
            kwargs['gender'] = gender

            body_model_gendered[gender] = smplx.create(
                model_type='smpl',
                model_path=human_model_path,
                **kwargs).to(self.device)
            
        pdb.set_trace()

        # ----------------initialize----------------

        # use HumanData to store the data
        human_data = HumanData()

        # initialize dict
        path_dict = {}
        for path_key in config['path']:
            path_dict[key] = []
        kps_dict = {}
        for kps_key in config['keypoints']:
            kps_dict[kps_key] = []
        bbox_dict = {}
        for bbox_key in config['bbox']:
            bbox_dict[bbox_key] = []
        camera_dict = {}
        for camera_key in config['camera']:
            camera_dict[camera_key] = []
        temporal_dict = {}
        for temporal_key in config['temporal']:
            temporal_dict[temporal_key] = []
        
        # smpl or smplx dict here
        smpl_dict = {}
        for key in self.smpl_shape.keys():
            smpl_dict[key] = []

        # prepare random id  list for track id
        seed = metadata['date']
        random_ids = np.random.RandomState(seed=int(seed)).permutation(999999)
        used_id_num = 0

        # dataset specific & test area
        skip_count = 0
        target_seqs = []


        # ----------------parse dataset----------------

        # parse sequences
        seqs = glob.glob(os.path.join(dataset_path, 'P*', '*_*'))

        for seq in seqs:
            # track_id = random_ids[used_id_num]
            # seq_name = os.path.basename(seq)
            # used_id_num += 1
            
            # load sequence annotation
            data_file = glob.glob(os.path.join(seq, "*_data.pkl"))[0]
            with open(data_file, "rb") as f:
                seq_anno = pickle.load(f)

            if mode == 'else':
                if seq_anno['emdb1'] == 1 or seq_anno['emdb2'] == 1:
                    skip_count += 1
                    continue
            elif not seq_anno[mode]:
                skip_count += 1
                continue

            target_seqs.append(seq)
        #     continue
        # pdb.set_trace()

        # return

        for seq in tqdm(target_seqs, position=0, leave=False, desc='Processing sequences'):
        # for seq in target_seqs:

            track_id = random_ids[used_id_num]
            seq_name = os.path.basename(seq)
            used_id_num += 1
            
            # load sequence annotation
            data_file = glob.glob(os.path.join(seq, "*_data.pkl"))[0]
            with open(data_file, "rb") as f:
                seq_anno = pickle.load(f)
            # load keypoints (N, 24, 2)
            j2d_seq = seq_anno['kp2d']  
            frame_length = len(j2d_seq)

            # load bbox (N, 4) xyxy -> xywh (N, 5)
            seq_bbox = seq_anno['bboxes']['bboxes']
            seq_bbox_invalid = seq_anno['bboxes']['invalid_idxs']
            bbox_mask = [1 if i not in seq_bbox_invalid 
                         else 0 for i in range(len(seq_bbox))]
            bbox_xywh = [self._xyxy2xywh(box) + [bbox_mask[i]]
                         for i, box in enumerate(seq_bbox)]

            # load frame mask
            frame_mask = seq_anno['good_frames_mask']

            # load camera parameters
            seq_cam = seq_anno['camera']

            intrinsics = seq_anno["camera"]["intrinsics"]
            focal_length = [intrinsics[0, 0], intrinsics[1, 1]]
            principal_point = [intrinsics[0, 2], intrinsics[1, 2]]

            extrinsics = seq_anno["camera"]["extrinsics"]
            width, height = seq_anno["camera"]["width"], seq_anno["camera"]["height"]

            # build camera
            camera = build_cameras(
                dict(
                    type='PerspectiveCameras',
                    convention='opencv',
                    in_ndc=False,
                    focal_length=focal_length,
                    image_size=(width, height),
                    principal_point=principal_point)).to(self.device)

            # load gender and smpl parameters
            seq_gender = seq_anno['gender']
            seq_smpl = seq_anno['smpl']
            smpl_params = {}
            for key in self.smpl_mapping.keys():
                smpl_params[key] = seq_smpl[self.smpl_mapping[key]] 
            # pdb.set_trace()
            smpl_params['betas'] = smpl_params['betas'].reshape(-1,10).repeat(frame_length, axis=0)
            
            passed = 0
            # parse through frames
            # for fid in range(frame_length):
            for fid in tqdm(range(frame_length), position=1, 
                            leave=False, desc='Processing frames'):
                if frame_mask[fid] == 0:
                    passed+=1
                    continue

                # prepare image path
                imgp = os.path.join(seq, 'images', f"{'{:05d}'.format(fid)}.jpg")
                image_path = imgp.replace(f'{dataset_path}{os.path.sep}', '')
                
                # extract smpl param
                smpl_param = {}
                for key in self.smpl_shape.keys():
                    smpl_param[key] = smpl_params[key][fid]
                
                # prepare smpl
                body_model_param_tensor = {key: torch.tensor(
                    np.array(smpl_param[key]).reshape(self.smpl_shape[key]),
                            device=self.device, dtype=torch.float32)
                            for key in self.smpl_shape.keys()
                            if len(smpl_param[key]) > 0}
                output = smpl_gendered[seq_gender](**body_model_param_tensor, return_verts=True)
                smpl_joints = output['joints']
                kps3d = smpl_joints.detach().cpu().numpy()

                # get pelvis in world frame
                pelvis_world = kps3d[0, get_keypoint_idx('pelvis', 'smpl')]
                global_orient_c, transl_c = transform_to_camera_frame(
                    global_orient=smpl_param['global_orient'],
                    transl=smpl_param['transl'],
                    pelvis=pelvis_world,
                    extrinsic=extrinsics[fid],)
                
                # update smpl param
                smpl_param['global_orient'] = global_orient_c
                smpl_param['transl'] = transl_c

                # update smpl
                body_model_param_tensor = {key: torch.tensor(
                    np.array(smpl_param[key]).reshape(self.smpl_shape[key]),
                            device=self.device, dtype=torch.float32)
                            for key in self.smpl_shape.keys()
                            if len(smpl_param[key]) > 0}
                output = smpl_gendered[seq_gender](**body_model_param_tensor, return_verts=True)
                smpl_joints = output['joints']
                kps3d = smpl_joints.detach().cpu().numpy()
                kps2d = camera.transform_points_screen(smpl_joints)[..., :2].detach().cpu().numpy()

                j2d = j2d_seq[fid]

                # test 2d overlay
                # img = cv2.imread(f'{dataset_path}/{image_path}')
                # for kp in kps2d[0]:
                #     if  0 < kp[0] < width and 0 < kp[1] < height: 
                #         cv2.circle(img, (int(kp[0]), int(kp[1])), 3, (0,0,255), 1)
                #     pass
                # for kp in j2d:
                #     if  0 < kp[0] < width and 0 < kp[1] < height: 
                #         cv2.circle(img, (int(kp[0]), int(kp[1])), 3, (255,0,0), 1)
                #     pass
                # # write image
                # os.makedirs(f'{out_path}', exist_ok=True)
                # cv2.imwrite(f'{out_path}/{os.path.basename(seq)}_{fid}.jpg', img)
                # pdb.set_trace()

                # image path
                image_path_.append(image_path)

                # bbox
                bboxs_['bbox_xywh'].append(bbox_xywh[fid])

                # keypoints
                keypoints2d_smpl_.append(kps2d[0])
                keypoints3d_smpl_.append(kps3d[0])
                keypoints2d_original_.append(j2d)

                # smpl parameters
                for key in self.smpl_shape.keys():
                    smpl_[key].append(smpl_param[key])

                # camera parameters
                meta_['focal_length'].append(focal_length)
                meta_['principal_point'].append(principal_point)
                meta_['width'].append(width)
                meta_['height'].append(height)
                meta_['gender'].append(seq_gender)
                meta_['track_id'].append(track_id)
                meta_['frame_id'].append(fid)   
                meta_['sequence_name'].append(seq_name)
                meta_['RT'].append(extrinsics[fid])

                size_i = min(size, len(target_seqs))

            # print(os.path.basename(seq), passed, frame_length)

        # meta
        human_data['meta'] = meta_

        # image path
        human_data['image_path'] = image_path_

        # save bbox
        for bbox_name in bboxs_.keys():
            bbox_ = np.array(bboxs_[bbox_name]).reshape(-1, 5)
            human_data[bbox_name] = bbox_

        # save smplx
        # human_data.skip_keys_check = ['smplx']
        for key in smpl_.keys():
            smpl_[key] = np.concatenate(
                smpl_[key], axis=0).reshape(self.smpl_shape[key])
        human_data['smpl'] = smpl_

        # keypoints2d_smpl
        keypoints2d_smpl = np.concatenate(
            keypoints2d_smpl_, axis=0).reshape(-1, 45, 2)
        keypoints2d_smpl_conf = np.ones([keypoints2d_smpl.shape[0], 45, 1])
        keypoints2d_smpl = np.concatenate(
            [keypoints2d_smpl, keypoints2d_smpl_conf], axis=-1)
        keypoints2d_smpl, keypoints2d_smpl_mask = \
                convert_kps(keypoints2d_smpl, src='smpl_45', dst='human_data')
        human_data['keypoints2d_smpl'] = keypoints2d_smpl
        human_data['keypoints2d_smpl_mask'] = keypoints2d_smpl_mask

        # keypoints3d_smpl
        keypoints3d_smpl = np.concatenate(
            keypoints3d_smpl_, axis=0).reshape(-1, 45, 3)
        keypoints3d_smpl_conf = np.ones([keypoints3d_smpl.shape[0], 45, 1])
        keypoints3d_smpl = np.concatenate(
            [keypoints3d_smpl, keypoints3d_smpl_conf], axis=-1)
        keypoints3d_smpl, keypoints3d_smpl_mask = \
                convert_kps(keypoints3d_smpl, src='smpl_45', dst='human_data')
        human_data['keypoints3d_smpl'] = keypoints3d_smpl
        human_data['keypoints3d_smpl_mask'] = keypoints3d_smpl_mask

        # keypoints2d_original
        keypoints2d_original = np.concatenate(
            keypoints2d_original_, axis=0).reshape(-1, 24, 2)
        keypoints2d_original_conf = np.ones([keypoints2d_original.shape[0], 24, 1])
        keypoints2d_original = np.concatenate(
            [keypoints2d_original, keypoints2d_original_conf], axis=-1)
        keypoints2d_original, keypoints2d_original_mask = \
                convert_kps(keypoints2d_original, src='smpl_24', dst='human_data')
        human_data['keypoints2d_original'] = keypoints2d_original
        human_data['keypoints2d_original_mask'] = keypoints2d_original_mask

        # misc
        human_data['misc'] = self.misc_config
        human_data['config'] = f'emdb_{mode}'

        # save
        human_data.compress_keypoints_by_mask()
        os.makedirs(out_path, exist_ok=True)
        out_file = os.path.join(
            out_path,
            f'emdb_{mode}_{seed}_{"{:02d}".format(size_i)}.npz')
        # human_data.dump(out_file)

        














