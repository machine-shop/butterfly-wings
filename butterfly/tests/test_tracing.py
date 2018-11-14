import numpy as np
import scipy.ndimage as ndi
from skimage.measure import regionprops
import pytest
from numpy.testing import assert_allclose

from butterfly import tracing


@pytest.fixture(scope="module")
def fake_butterfly():
    butterfly = np.zeros((100, 200))
    butterfly[25:50, 25:50] = 1  # left wing
    butterfly[25:50, 150:175] = 1  # right wing
    butterfly[50:90, 40:160] = 1  # body
    butterfly[25:50, 80:120] = 1  # head

    return butterfly


@pytest.fixture(scope="module")
def fake_shape():
    shape = np.zeros((5, 5))
    shape[1:, 4] = 1
    shape[2:4, 2] = 1
    shape[[1, 4], 3] = 1

    return shape


def test_moore_neighborhood():
    array = np.array([[10, 9], [9, 9], [9, 10], [9, 11],
                      [10, 11], [11, 11], [11, 10], [11, 9]])
    assert np.all(tracing.moore_neighborhood([10, 10], [10, 9]) == array)


def test_split(fake_butterfly):
    assert tracing.split_picture(fake_butterfly) in [99, 100]


def test_boundary_tracing(fake_shape):
    bound1 = np.array([[1, 3], [1, 4], [2, 4], [3, 4], [4, 4],
                       [4, 3], [3, 4], [2, 4]])
    bound2 = np.array([[1, 3], [1, 4], [2, 4], [3, 4], [4, 4],
                       [4, 3], [3, 2], [2, 2]])
    labels1, _ = ndi.label(fake_shape,
                           structure=ndi.generate_binary_structure(2, 1))
    labels2, _ = ndi.label(fake_shape,
                           structure=ndi.generate_binary_structure(2, 2))

    regions1 = regionprops(labels1)
    regions2 = regionprops(labels2)

    boundary1 = tracing.boundary_tracing(regions1[0])
    boundary2 = tracing.boundary_tracing(regions2[0])

    assert np.all(boundary1 == bound1)
    assert np.all(boundary2 == bound2)


def test_fourier_descriptors(n_descriptors=15):
    expected_positive = np.array([9.3220e+03 + 1.1682e+04j,
                                  -5.6435e+03 - 5.6435e+03j,
                                  0,
                                  0,
                                  -5.4001e-12 - 5.9685e-12j,
                                  -2.2606e+02 - 2.2606e+02j,
                                  0,
                                  0], dtype=complex)

    expected_negative = np.array([-1.1550e+02 - 1.1550e+02j,
                                  0,
                                  0,
                                  -5.4001e-12-5.9685e-12j,
                                  -6.2735e+02-6.2735e+02j,
                                  0,
                                  0], dtype=complex)

    binary = np.zeros((100, 100), dtype=bool)
    binary[20:80, 10:70] = 1
    labels, _ = ndi.label(binary,
                          structure=ndi.generate_binary_structure(2, 1))
    regions = regionprops(labels)
    boundary = tracing.boundary_tracing(regions[0])
    print(boundary.shape)
    descriptors = tracing.fourier_descriptors(boundary)
    print(descriptors.shape)
    print(descriptors)

    assert_allclose(descriptors[:1+n_descriptors//2],
                    expected_positive, rtol=0.1)

    assert_allclose(descriptors[1+(-n_descriptors//2):],
                    expected_negative, rtol=0.1)


def test_detect_points_interest(fake_butterfly):
    middle = tracing.split_picture(fake_butterfly)
    fake_butterfly[:, middle] = 0
    labels, _ = ndi.label(fake_butterfly,
                          structure=ndi.generate_binary_structure(2, 2))
    regions = regionprops(labels)
    boundary_l = tracing.boundary_tracing(regions[0])
    boundary_r = tracing.boundary_tracing(regions[1])

    test_poi_l = np.array([[25, 25], [49, 80]])
    test_poi_r = np.array([[25, 174], [49, 119]])
    poi_l = tracing.detect_points_interest(boundary_l, 'l', 200)
    poi_r = tracing.detect_points_interest(boundary_r, 'r', 200)

    assert np.all(poi_r[0] == test_poi_r[0])
    assert np.all(poi_l[0] == test_poi_l[0])
    assert np.all(poi_r[1] == test_poi_r[1])
    assert np.all(poi_l[1] == test_poi_l[1])
