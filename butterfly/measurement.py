import numpy as np
from joblib import Memory

location = './cachedir'
memory = Memory(location, verbose=0)


@memory.cache()
def main(points_interest, T_space, axes):
    ''' Calculates the length and draws the lines for length
    of the butterfly wings.

    Parameters
    ----------
    ax: array
        the array containing the 3 intermediary Axes.
    points_interest: array
        the array containing the four points of interest,
        each of which is a coordinate specifying the start/end
        point of the left/right wing.
    T_space: float
        number of pixels between 2 ticks.

    Returns
    -------
    ax: ax
        an ax object
    dst_pix: tuple
        the tuple contains the distance of the left/right wing
        distance in pixels
    dst_mm: tuple
        the tuple contains the distance of the left/right wing
        distance in millimeters

    '''

    pix_out_l, pix_in_l, pix_out_r, pix_in_r = points_interest
    dist_r_pix = np.sqrt((pix_out_r[0] - pix_in_r[0]) ** 2
                         + (pix_out_r[1] - pix_in_r[1]) ** 2)
    dist_l_pix = np.sqrt((pix_out_l[0] - pix_in_l[0]) ** 2
                         + (pix_out_l[1] - pix_in_l[1]) ** 2)

    # Converting to millimeters
    dist_l_mm = round(dist_l_pix / T_space, 2)
    dist_r_mm = round(dist_r_pix / T_space, 2)

    # Do we want to round these?
    dist_l_pix = round(dist_l_pix, 2)
    dist_r_pix = round(dist_r_pix, 2)

    dst_pix = (dist_l_pix, dist_r_pix)
    dst_mm = (dist_l_mm, dist_r_mm)

    if axes[0]:
        textsize = 7
        if axes[3]:
            textsize = 4
        axes[0].plot([pix_out_l[1], pix_in_l[1]],
                     [pix_out_l[0], pix_in_l[0]], color='r')
        axes[0].plot([pix_out_r[1], pix_in_r[1]],
                     [pix_out_r[0], pix_in_r[0]], color='r')
        axes[0].text(int((pix_out_l[1] + pix_in_l[1]) / 2) + 50,
                     int((pix_out_l[0] + pix_in_l[0]) / 2) - 50,
                     'dist_left = ' + str(round(dist_l_mm, 2)) + ' mm',
                     size=textsize,
                     color='r')
        axes[0].text(int((pix_out_r[1] + pix_in_r[1]) / 2) + 50,
                     int((pix_out_r[0] + pix_in_r[0]) / 2) + 50,
                     'dist_right = ' + str(round(dist_r_mm, 2))
                     + ' mm',
                     size=textsize, color='r')

    print(f'left_wing : {dst_mm[0]} mm')
    print(f'right_wing : {dst_mm[1]} mm')

    return dst_pix, dst_mm
