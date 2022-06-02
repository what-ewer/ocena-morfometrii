import numpy as np
from vis_utils import VolumeVisualizer, ColorMapVisualizer
import matplotlib.pyplot as plt
from PIL import Image
from skimage.morphology import skeletonize_3d
from scipy.ndimage import zoom

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

    @staticmethod
    def vascular_network_area(reconstruction_projection_mask):
        plt.figure(figsize=(15, 10))
        plt.title('vascular network area 2d')
        im = Image.fromarray(reconstruction_projection_mask.T)
        im.save("results/vascular_network_2d.png")

    @staticmethod
    def vascular_density(convex_projection):
        plt.figure(figsize=(15, 10))
        plt.title('convex projection')
        im = Image.fromarray(convex_projection.T)
        im.save("results/convex_projection.png")

    @staticmethod
    def visualize_contours(scales, contours_lengths, rec_mask, proj_contour_func):
        plt.figure(figsize=(10, 40))
        for i, scale in enumerate(scales):
            proj = zoom(rec_mask, scale, order=0)
            contour = proj_contour_func()
            plt.subplot(len(scales), 2, 2 * i + 1)
            plt.imshow(proj.T)
            plt.subplot(len(scales), 2, 2 * i + 2)
            plt.imshow(contour.T)
            contours_lengths.append(int(np.sum(contour)))
        plt.savefig('results/contours_scaled')
        plt.clf()
        return scales, contours_lengths

    @staticmethod
    def scales_contour_lengths(scales, contours_lengths, lm):
        plt.figure(figsize=(11, 7))
        plt.scatter(np.log(scales), np.log(contours_lengths), s=30)
        plt.plot(np.log(scales), lm.predict(np.log(scales).reshape(-1, 1)), color='red')
        plt.xlabel('log(scaling_factor)')
        plt.ylabel('log(contour_area)')
        plt.savefig('results/scales_contour_corelation')
        plt.clf()