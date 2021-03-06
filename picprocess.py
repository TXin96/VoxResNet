import os
import nibabel as nib
import scipy.ndimage.filters as filter
import numpy as np
import cv2


def pic_process(source_path, result_path):
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    img_path = source_path
    imgs = []
    affines = []
    files = os.listdir(img_path)
    for file in files:
        if file.endswith('.nii.gz') or file.endswith('.nii'):
            img = nib.load(img_path + '/' + file)
            imgs.append(img.get_data()[:, :, :, 0])
            affines.append(img.affine)

    for i in range(0, len(imgs)):
        img3d = imgs[i]
        affine = affines[i]
        file = files[i]
        x = img3d.shape[0]
        y = img3d.shape[1]
        z = img3d.shape[2]

        # Gaussian Filter
        smoothed3d = filter.gaussian_filter(img3d, 0.7)

        max = np.amax(smoothed3d)
        min = np.amin(smoothed3d)

        # Convert to 8bit
        smoothed3d = (smoothed3d - min) * 255.0 / float(max - min)
        smoothed3d = np.uint8(smoothed3d)

        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=4.5)
        for i in range(0, z):
            smoothed3d[:, :, i] = clahe.apply(smoothed3d[:, :, i])

        # Convert back to 16bit
        smoothed3d = np.int16(smoothed3d)
        smoothed3d = smoothed3d * float(max - min) / 255.0 + min

        # Normalized
        average = np.mean(smoothed3d)
        stndrd_var = np.std(smoothed3d)
        smoothed3d = (smoothed3d - average) / stndrd_var

        # Output
        enhanced3d = smoothed3d.reshape((x, y, z, 1))
        img3dnii = nib.Nifti1Image(enhanced3d, affine)
        nib.save(img3dnii, result_path + '/' + file)
