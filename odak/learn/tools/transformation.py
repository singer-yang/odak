import math
import torch


def rotmatx(angle):
    """
    Definition to generate a rotation matrix along X axis.

    Parameters
    ----------
    angle        : torch.tensor
                   Rotation angles in degrees.

    Returns
    ----------
    rotx         : torch.tensor
                   Rotation matrix along X axis.
    """
    angle = torch.deg2rad(angle)
    rotx = torch.tensor([
                         [1.,               0.,               0.],
                         [0.,  math.cos(angle), -math.sin(angle)],
                         [0.,  math.sin(angle),  math.cos(angle)]
                        ], device = angle.device)
    return rotx


def rotmaty(angle):
    """
    Definition to generate a rotation matrix along Y axis.

    Parameters
    ----------
    angle        : torch.tensor
                   Rotation angles in degrees.

    Returns
    ----------
    roty         : torch.tensor
                   Rotation matrix along Y axis.
    """
    angle = torch.deg2rad(angle)
    roty = torch.tensor([
                         [math.cos(angle),  0., math.sin(angle)],
                         [0.,               1.,              0.],
                         [-math.sin(angle), 0., math.cos(angle)]
                        ], device = angle.device)
    return roty


def rotmatz(angle):
    """
    Definition to generate a rotation matrix along Z axis.

    Parameters
    ----------
    angle        : torch.tensor
                   Rotation angles in degrees.

    Returns
    ----------
    rotz         : torch.tensor
                   Rotation matrix along Z axis.
    """
    angle = torch.deg2rad(angle)
    rotz = torch.tensor([
                         [math.cos(angle), -math.sin(angle), 0.],
                         [math.sin(angle),  math.cos(angle), 0.],
                         [             0.,               0., 1.]
                        ], device = angle.device)
    return rotz


def get_rotation_matrix(tilt_angles = [0., 0., 0.], tilt_order = 'XYZ'):
    """
    Function to generate rotation matrix for given tilt angles and tilt order.


    Parameters
    ----------
    tilt_angles        : list
                         Tilt angles in degrees along XYZ axes.
    tilt_order         : str
                         Rotation order (e.g., XYZ, XZY, ZXY, YXZ, ZYX).

    Returns
    -------
    rotmat             : torch.tensor
                         Rotation matrix.
    """
    rotx = rotmatx(tilt_angles[0])
    roty = rotmaty(tilt_angles[1])
    rotz = rotmatz(tilt_angles[2])
    if tilt_order =='XYZ':
        rotmat = torch.mm(rotz,torch.mm(roty, rotx))
    elif tilt_order == 'XZY':
        rotmat = torch.mm(roty,torch.mm(rotz, rotx))
    elif tilt_order == 'ZXY':
        rotmat = torch.mm(roty,torch.mm(rotx, rotz))
    elif tilt_order == 'YXZ':
        rotmat = torch.mm(rotz,torch.mm(rotx, roty))
    elif tilt_order == 'ZYX':
         rotmat = torch.mm(rotx,torch.mm(roty, rotz))
    return rotmat


def rotate_points(
                 point,
                 angles = torch.tensor([[0, 0, 0]]), 
                 mode='XYZ', 
                 origin = torch.tensor([[0, 0, 0]]), 
                 offset = torch.tensor([[0, 0, 0]])
                ):
    """
    Definition to rotate a given point. Note that rotation is always with respect to 0,0,0.

    Parameters
    ----------
    point        : torch.tensor
                   A point with size of [3] or [1, 3] or [m, 3].
    angles       : torch.tensor
                   Rotation angles in degrees. 
    mode         : str
                   Rotation mode determines ordering of the rotations at each axis. There are XYZ,YXZ,ZXY and ZYX modes.
    origin       : torch.tensor
                   Reference point for a rotation.
                   Expected size is [3] or [1, 3].
    offset       : torch.tensor
                   Shift with the given offset.
                   Expected size is [3] or [1, 3] or [m, 3].

    Returns
    ----------
    result       : torch.tensor
                   Result of the rotation [1 x 3] or [m x 3].
    rotx         : torch.tensor
                   Rotation matrix along X axis [3 x 3].
    roty         : torch.tensor
                   Rotation matrix along Y axis [3 x 3].
    rotz         : torch.tensor
                   Rotation matrix along Z axis [3 x 3].
    """
    if len(point.shape) == 1:
        point = point.unsqueeze(0)
    if len(angles.shape) == 1:
        angles = angles.unsqueeze(0)
    rotx = rotmatx(angles[:, 0])
    roty = rotmaty(angles[:, 1])
    rotz = rotmatz(angles[:, 2])
    point -= origin
    if mode == 'XYZ':
        result = torch.mm(rotz, torch.mm(roty, torch.mm(rotx, point.T))).T
    elif mode == 'XZY':
        result = torch.mm(roty, torch.mm(rotz, torch.mm(rotx, point.T))).T
    elif mode == 'YXZ':
        result = torch.mm(rotz, torch.mm(rotx, torch.mm(roty, point.T))).T
    elif mode == 'ZXY':
        result = torch.mm(roty, torch.mm(rotx, torch.mm(rotz, point.T))).T
    elif mode == 'ZYX':
        result = torch.mm(rotx, torch.mm(roty, torch.mm(rotz, point.T))).T
    result += origin
    result += offset
    return result.to(point.device), rotx, roty, rotz


def tilt_towards(location, lookat):
    """
    Definition to tilt surface normal of a plane towards a point.

    Parameters
    ----------
    location     : list
                   Center of the plane to be tilted.
    lookat       : list
                   Tilt towards this point.

    Returns
    ----------
    angles       : list
                   Rotation angles in degrees.
    """
    dx = location[0]-lookat[0]
    dy = location[1]-lookat[1]
    dz = location[2]-lookat[2]
    dist = torch.sqrt(torch.tensor(dx**2+dy**2+dz**2))
    phi = torch.atan2(torch.tensor(dy), torch.tensor(dx))
    theta = torch.arccos(dz/dist)
    angles = [
        0,
        float(torch.rad2deg(theta)),
        float(torch.rad2deg(phi))
    ]
    return angles
