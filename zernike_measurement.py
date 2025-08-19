import numpy as np
from wfs import WFS

radial_order_ANSI = np.array([0,1,1,2,2,2,3,3,3,3,4,4,4,4,4])
azimuthal_order_ANSI = np.array([0,-1,1,-2,0,2,-3,-1,1,3,-4,-2,0,2,4])

def convert_ANSI_to_knoll(zernike_matrix):
    
    """
    Takes matrix of Zernike coefficients as outputted by the extract_zernike_coeffs function in the ANSI convention used
    by the Shack-Hartmann software and outputs a matrix re-ordered in the Knoll convention used by the diffractio package
    """

    converted_radial = zernike_matrix[:, 0].astype(int)
    converted_azimuthal = np.array((0, 1, -1, 0, -2, 2, -1, 1, -3, 3, 0, 2, -2, 4, -4))
    converted_coefficients = np.empty(15) # Create array to store converted coefficients from ANSI to Knoll indexing convention

    for i in np.arange(15):
        if zernike_matrix[i, 0]==0:
            converted_coefficients[0] = zernike_matrix[i, 2]
        elif zernike_matrix[i, 0]==1:
            if zernike_matrix[i, 1]==1:
                converted_coefficients[1] = zernike_matrix[i, 2]
            else:
                converted_coefficients[2] = zernike_matrix[i, 2]
        elif zernike_matrix[i, 0]==2:
            if zernike_matrix[i, 1]==0:
                converted_coefficients[3] = zernike_matrix[i, 2]
            elif zernike_matrix[i, 1]==-2:
                converted_coefficients[4] = zernike_matrix[i, 2]
            else:
                converted_coefficients[5] = zernike_matrix[i, 2]
        elif zernike_matrix[i, 0]==3:
            if zernike_matrix[i, 1]==-1:
                converted_coefficients[6] = zernike_matrix[i, 2]
            elif zernike_matrix[i, 1]==1:
                converted_coefficients[7] = zernike_matrix[i, 2]
            elif zernike_matrix[i, 1]==-3:
                converted_coefficients[8] = zernike_matrix[i, 2]
            else:
                converted_coefficients[9] = zernike_matrix[i, 2]
        else:
            if zernike_matrix[i, 1]==0:
                converted_coefficients[10] = zernike_matrix[i, 2]
            elif zernike_matrix[i, 1]==2:
                converted_coefficients[11] = zernike_matrix[i, 2]
            elif zernike_matrix[i, 1]==-2:
                converted_coefficients[12] = zernike_matrix[i, 2]
            elif zernike_matrix[i, 1]==4:
                converted_coefficients[13] = zernike_matrix[i, 2]
            else:
                converted_coefficients[14] = zernike_matrix[i, 2]
    
    converted_zernike_matrix = np.column_stack((converted_radial, converted_azimuthal, converted_coefficients))
    return converted_zernike_matrix

# Initialize the device
wfs = WFS()

# Connect to the WFS20-5C
wfs.connect()

# Configure camera resolution for WFS20-5C
wfs._configure_cam(cam_resolution_index=0) 
# 0: 2048x2048
# 1: 1536x1536
# 2: 1024x1024
# 3: 768x768
# 4: 512x512
# 5: 360x360

# Set exposure and gain
wfs._set_exposure_time(0.8)    # ms
wfs._set_master_gain(1)       # fixed for WFS20

# Set pupil
wfs._set_pupil(0.2, -0.3, 9.547, 9.547) # mm
# x and y center coordinates, x and y diameter

# Set noise cut and black level to AUTO
wfs.dynamic_noise_cut.value = 1       # enable dynamic noise cut
#wfs.allow_auto_exposure.value = 1     # auto exposure/gain control

file_base = 'zernike_measurement'

# Average over 100 images
wfs._average_image(100)

# Wait until averaging is completed
while wfs.average_data_ready.value == 0:
    wfs._average_image(100)

wfs.update()

meas_zernike_coefficients = np.array(wfs.array_zernike_um[1:16])
zernike_matrix = np.column_stack((radial_order_ANSI, azimuthal_order_ANSI, meas_zernike_coefficients))
zernike_matrix = convert_ANSI_to_knoll(zernike_matrix)

# meas_wavefront = wfs._calc_wavefront(wavefront_type=0, limit_to_pupil=1)

np.savetxt(file_base + '.csv', zernike_matrix, delimiter=",")

wfs.disconnect()