import numpy as np
from skimage.filters import threshold_otsu
from scipy import ndimage as ndi
from skimage.measure import regionprops
import skimage.color as color
from skimage.exposure import rescale_intensity
from joblib import Memory
location = './cachedir'
memory = Memory(location, verbose=0)


def find_tags_edge(binary, top_ruler):
    """Find the edge between the tag area on the right and the butterfly area
    and returns the corresponding x coordinate of that vertical line

    Arguments
    ---------
    binary : 2D array
        Binarized image of the entire RGB image
    top_ruler : int
        Y-coordinate of the top of the ruler

    Returns
    -------
    crop_right : int
        x coordinate of the vertical line separating the tags area from the
        butterfly area
    """
    lower_bound = top_ruler - int(binary.shape[0] * 0.1)
    left_bound = int(binary.shape[1] * 0.5)
    focus = binary[:lower_bound, left_bound:]

    markers = ndi.label(focus,
                        structure=ndi.generate_binary_structure(2, 1))[0]
    
    regions = regionprops(markers)
    biggest_areas = [(i, region.area) for i, region in enumerate(regions)]
    biggest_areas.sort(key=lambda x: x[1], reverse=True)
    
    filtered_regions = []
    for i, area in biggest_areas[1:5]:
        if regions[i].extent>0.8:
            filtered_regions.append(regions[i])

    left_pixels = [np.min(region.coords[:, 1]) for region in filtered_regions]
    left_pixels = np.array(left_pixels)
    left_pixels = left_pixels[left_pixels > 0.05 * binary.shape[1]]

    crop_right = int(0.5 * binary.shape[1] + np.min(left_pixels))

    return crop_right


@memory.cache()
def main(image_rgb, top_ruler):
    """Binarizes and crops properly image_rgb

    Arguments
    ---------
    image_rgb : 3D array
        RGB image of the entire picture
    top_ruler: integer
        Y-coordinate of the height of the ruler top edge as
        found by ruler_detection.py
    ax : obj
        If any, the result of the binarization and cropping
        will be plotted on it

    Returns
    -------
    bfly_bin : 2D array
        Binarized and cropped version of imge_rgb
    """

    image_gray = image_rgb[:, :, 0]
    thresh_rgb = threshold_otsu(image_gray, nbins=60)
    binary = image_gray > thresh_rgb

    label_edge = find_tags_edge(binary, top_ruler)

    bfly_rgb = image_rgb[:top_ruler, :label_edge]
    bfly_hsv = color.rgb2hsv(bfly_rgb)[:, :, 1]
    rescaled = rescale_intensity(bfly_hsv, out_range=(0, 255))
    thresh_hsv = threshold_otsu(rescaled)
    bfly_bin = rescaled > thresh_hsv
    return bfly_bin
