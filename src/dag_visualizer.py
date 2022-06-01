import numpy as np
from vis_utils import VolumeVisualizer, ColorMapVisualizer
from skimage.morphology import skeletonize_3d

class DAG_Visualizer:
    @staticmethod
    def visualize_addition(base, base_with_addition):
        base = (base.copy() > 0).astype(np.uint8)
        addition = (base_with_addition > 0).astype(np.uint8)
        addition[base == 1] = 0
        ColorMapVisualizer(base + addition * 4).visualize()
        
    @staticmethod
    def visualize_lsd(lsd_mask):
        ColorMapVisualizer(lsd_mask.astype(np.uint8)).visualize()
        
    @staticmethod
    def visualize_gradient(lsd_mask):
        ColorMapVisualizer(lsd_mask.astype(np.uint8)).visualize(gradient=True)
        
    @staticmethod
    def visualize_mask_bin(mask):
        VolumeVisualizer((mask > 0).astype(np.uint8), binary=True).visualize()
        
    @staticmethod
    def visualize_mask_non_bin(mask):
        VolumeVisualizer((mask > 0).astype(np.uint8) * 255, binary=False).visualize()
        
    @staticmethod
    def visualize_skeleton(mask, visualize_mask=True, visualize_both_versions=False):
        skeleton = skeletonize_3d((mask > 0).astype(np.uint8))
        if not visualize_mask or visualize_both_versions:
            VolumeVisualizer(skeleton, binary=True).visualize()
        if visualize_mask or visualize_both_versions:
            skeleton = skeleton.astype(np.uint8) * 4
            mask = (mask > 0).astype(np.uint8) * 3
            mask[skeleton != 0] = 0
            ColorMapVisualizer(skeleton + mask).visualize()

    @staticmethod
    def visualize_ultimate(lsd, base_mask):
        DAG_Visualizer.visualize_lsd(lsd)
        DAG_Visualizer.visualize_mask_non_bin(lsd)
        DAG_Visualizer.visualize_addition(base_mask, lsd)
        DAG_Visualizer.visualize_skeleton(lsd, visualize_mask=True)