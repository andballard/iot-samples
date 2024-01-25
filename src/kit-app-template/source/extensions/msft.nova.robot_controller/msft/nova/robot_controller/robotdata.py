from typing import List


class ArmType:
    KHI_RS007N = 0
    KHI_RS007L = 1
    KHI_RS007N_URDF = 2
    KHI_RS007L_URDF = 3
    UR10 = 4
    UR5 = 5
    UR10e = 6
    UR5e = 7
    UR3e = 8


angles = ['ang1j', 'ang2j', 'ang3j', 'ang4j', 'ang5j', 'ang6j']


robot_configs = [
    {
        'id': 'robot1',
        'armType': ArmType.KHI_RS007N,
        'baseLink': '/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        'linknames': ['link1piv.003', 'link2piv.003', 'link3piv.003', 'link4piv.003', 'link5piv.003', 'link6piv.003'],
    },
    {
        'id': 'robot2',
        'armType': ArmType.KHI_RS007N,
        'baseLink': '/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        'linknames': ['link1piv.001', 'link2piv.001', 'link3piv.001', 'link4piv.001', 'link5piv.001', 'link6piv.001'],
    },
    {
        'id': 'robot3',
        'armType': ArmType.KHI_RS007N,
        'baseLink': '/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        'linknames': ['link1piv.002', 'link2piv.002', 'link3piv.002', 'link4piv.002', 'link5piv.002', 'link6piv.002'],
    },
    {
        'id': 'robot4',
        'armType': ArmType.KHI_RS007N,
        'baseLink': '/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        'linknames': ['link1piv', 'link2piv', 'link3piv', 'link4piv', 'link5piv', 'link6piv'],
    },
    {
        'id': 'UR10e',
        'armType': ArmType.UR10e,
        'baseLink': '/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        'linknames': ['shoulder_link', 'upper_arm_link', 'forearm_link', 'wrist_1_link',
                      'wrist_2_link', 'wrist_3_link'],
    },
    {
        'id': 'UR3e',
        'armType': ArmType.UR3e,
        'baseLink': '/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        'linknames': ['shoulder_link.001', 'upper_arm_link.001', 'forearm_link.001', 'wrist_1_link.001',
                      'wrist_2_link.001', 'wrist_3_link.001'],
    },
    {
        'id': 'RS7URDF',
        'armType': ArmType.KHI_RS007N_URDF,
        'baseLink': '/World/PCR_8FT2_Only_Robot/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        'linknames': ['link1', 'link2', 'link3', 'link4', 'link5', 'link6'],
    }
]


def map_input_robot_data_to_motions(data: dict) -> List[List[float]]:
    return [[index, data[angle]] for index, angle in enumerate(angles)]


def map_input_robot_data_to_pose(data: dict) -> List[float]:
    return [data[key] for key in angles]


poses = {}


class RobotPose:
    zero = "zero"
    deg10 = "deg10"
    rest = "rest"
    fcartup = "fcartup"
    fcartdn = "fcartdn"
    ecartup = "ecartup"
    ecartdn = "ecartdn"
    key00up = "key00up"
    key00dn = "key00dn"
    key01up = "key01up"
    key01dn = "key01dn"
    key02up = "key02up"
    key02dn = "key02dn"
    key03up = "key03up"
    key03dn = "key03dn"
    key10up = "key10up"
    key10dn = "key10dn"
    key11up = "key11up"
    key11dn = "key11dn"
    key12up = "key12up"
    key12dn = "key12dn"
    key13up = "key13up"
    key13dn = "key13dn"
    key20up = "key20up"
    key20dn = "key20dn"
    key21up = "key21up"
    key21dn = "key21dn"
    key22up = "key22up"
    key22dn = "key22dn"
    key23up = "key23up"
    key23dn = "key23dn"
    Pose000000 = "Pose000000"
    Pose099900 = "Pose099900"
    Pose090000 = "Pose090000"
    Pose099999 = "Pose099999"
    Pose099000 = "Pose099000"
    Pose099990 = "Pose099990"
    Pose999999 = "Pose999999"


def DefineJointPose(pose, val):
    poses[pose] = val


def getPose(pose):
    LoadPoses()
    return poses[pose]


def LoadPoses():
    if poses:
        return

    DefineJointPose(RobotPose.zero, [0, 0, 0, 0, 0, 0])
    DefineJointPose(RobotPose.deg10, [10, 10, 10, 10, 10, 10])
    DefineJointPose(RobotPose.rest, [-16.805, 16.073, -100.892, 0, -63.021, 106.779])

    DefineJointPose(RobotPose.fcartup, [-26.76, 32.812, -74.172, 0, -73.061, 26.755])
    DefineJointPose(RobotPose.fcartdn, [-26.749, 40.511, -80.809, 0, -58.682, 26.75])

    DefineJointPose(RobotPose.ecartup, [-50.35, 49.744, -46.295, 0, -83.959, 50.347])
    DefineJointPose(RobotPose.ecartdn, [-50.351, 55.206, -54.692, 0, -70.107, 50.352])

    DefineJointPose(RobotPose.key00up, [-14.864, 26.011, -87.161, 0, -66.826, 102.537])
    DefineJointPose(RobotPose.key00dn, [-14.48, 28.642, -89.821, 0, -61.519, 104.49])
    DefineJointPose(RobotPose.key01up, [-16.88, 16.142, -101.146, 0, -62.727, 106.877])
    DefineJointPose(RobotPose.key01dn, [-16.808, 19.303, -103.537, 0, -57.146, 106.813])
    DefineJointPose(RobotPose.key02up, [-20.924, 3.754, -115.647, -0.001, -60.607, 110.92])
    DefineJointPose(RobotPose.key02dn, [-20.921, 7.105, -118.181, -0.001, -54.702, 110.919])
    DefineJointPose(RobotPose.key03up, [-25.945, -6.875, -125.815, -0.001, -61.063, 115.944])
    DefineJointPose(RobotPose.key03dn, [-25.942, -1.839, -129.447, -0.001, -52.394, 115.943])

    DefineJointPose(RobotPose.key10up, [-3.833, 24.123, -90.829, 0, -65.057, 93.834])
    DefineJointPose(RobotPose.key10dn, [-3.839, 27.028, -93.268, 0, -59.685, 93.835])
    DefineJointPose(RobotPose.key11up, [-4.485, 16.308, -106.377, 0, -57.305, 94.482])
    DefineJointPose(RobotPose.key11dn, [-4.487, 17.444, -107.108, 0, -55.446, 94.486])
    DefineJointPose(RobotPose.key12up, [-5.674, 2.826, -121.133, 0, -56.032, 95.67])
    DefineJointPose(RobotPose.key12dn, [-5.677, 4.939, -122.452, 0, -52.61, 95.675])
    DefineJointPose(RobotPose.key13up, [-7.204, -11.615, -129.863, 0, -61.795, 97.205])
    DefineJointPose(RobotPose.key13dn, [-7.207, -7.853, -132.776, 0, -55.074, 97.205])

    DefineJointPose(RobotPose.key20up, [7.072, 24.158, -89.905, 0, -65.933, 82.92])
    DefineJointPose(RobotPose.key20dn, [7.07, 27.478, -92.784, 0, -59.743, 82.929])
    DefineJointPose(RobotPose.key21up, [8.251, 16.929, -105.936, 0, -57.122, 81.753])
    DefineJointPose(RobotPose.key21dn, [8.249, 17.868, -106.538, 0, -55.594, 81.752])
    DefineJointPose(RobotPose.key22up, [8.251, 16.929, -105.936, 0, -57.122, 81.753])
    DefineJointPose(RobotPose.key22dn, [8.249, 17.868, -106.538, 0, -55.594, 81.752])
    DefineJointPose(RobotPose.key23up, [-7.204, -11.615, -129.863, 0, -61.795, 97.205])
    DefineJointPose(RobotPose.key23dn, [-7.207, -7.853, -132.776, 0, -55.074, 97.205])

    DefineJointPose(RobotPose.Pose000000, [0, 0, 0, 0, 0, 0])
    DefineJointPose(RobotPose.Pose099900, [0, -90, -90, -90, 0, 0])
    DefineJointPose(RobotPose.Pose090000, [0, -90, 0, 0, 0, 0])
    DefineJointPose(RobotPose.Pose099999, [0, -90, -90, -90, -90, -90])
    DefineJointPose(RobotPose.Pose099000, [0, -90, -90, 0, 0, 0])
    DefineJointPose(RobotPose.Pose099990, [0, -90, -90, -90, -90, 0])
    DefineJointPose(RobotPose.Pose999999, [-90, -90, -90, -90, -90, -90])
