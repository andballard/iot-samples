import math
import asyncio
from enum import Enum
from typing import List
# from babylonjs import Scene, TransformNode
import omni.usd
from pxr import Gf, UsdGeom
from .robotdata import RobotPose, getPose


class RotationalAxis(Enum):
    Zero = 0
    XPositive = 1
    XNegative = 2
    YPositive = 3
    YNegative = 4
    ZPositive = 5
    ZNegative = 6


class ArmType(Enum):
    KHI_RS007N = 0
    KHI_RS007L = 1
    KHI_RS007N_URDF = 2
    KHI_RS007L_URDF = 3
    URFamily = 4


class RobotMotion:
    def __init__(self, baseLink: str, linkNames: List[str], armType: ArmType = ArmType.KHI_RS007N):
        self.animating = True
        self.sequence = [
            RobotPose.zero, RobotPose.deg10, RobotPose.rest, RobotPose.fcartup, RobotPose.fcartdn,
            RobotPose.ecartup, RobotPose.ecartdn, RobotPose.key00up, RobotPose.key00dn, RobotPose.key01up,
            RobotPose.key01dn, RobotPose.key02up, RobotPose.key02dn, RobotPose.key03up, RobotPose.key03dn,
            RobotPose.zero, RobotPose.Pose099900, RobotPose.Pose090000, RobotPose.Pose099999,
            RobotPose.Pose099000, RobotPose.Pose099990, RobotPose.Pose999999]
        self.pos = 0
        self.lastPose = getPose(RobotPose.zero)
        self.pose = self.lastPose
        self.step = 1
        self.ms = 60
        self.fps = 1000 / self.ms
        self.curAng = [0, 0, 0, 0, 0, 0]
        self.armType = armType
        self.nlinks = 6
        self.linkNames = linkNames
        self.linkPaths = ['', '', '', '', '', '']
        self.isURDF = False
        self.rotAx = []
        self.rotAxKHI = [RotationalAxis.ZPositive, RotationalAxis.YNegative, RotationalAxis.YPositive,
                         RotationalAxis.ZPositive, RotationalAxis.YPositive, RotationalAxis.ZPositive]
        self.rotAxUR = [RotationalAxis.ZPositive, RotationalAxis.XNegative, RotationalAxis.XPositive,
                        RotationalAxis.XPositive, RotationalAxis.ZPositive, RotationalAxis.XPositive]
        self.rotAxKHIURDF = [RotationalAxis.ZPositive, RotationalAxis.ZNegative, RotationalAxis.ZPositive,
                             RotationalAxis.ZNegative, RotationalAxis.ZPositive, RotationalAxis.ZNegative]
        self.baseAxisURDF = [RotationalAxis.Zero, RotationalAxis.XNegative, RotationalAxis.Zero,
                             RotationalAxis.XNegative, RotationalAxis.XNegative, RotationalAxis.XNegative]
        self.jointMin = [-360, -90, -90, -360, -90, -360]
        self.jointMax = [+360, +90, +90, +360, +90, +360]
        self.jointOrg = [0, 0, 0, 0, 0, 0]
        self.jointSign = [1, 1, 1, 1, 1, 1]
        self.baseAngURDF = [0, 0, 0, 0, 0, 0]
        self.signs = [1, 1, 1, 1, 1, 1]
        self.timer = None
        self.currentPose = []

        if armType == ArmType.KHI_RS007N or armType == ArmType.KHI_RS007L:
            self.rotAx = self.rotAxKHI
            self.isURDF = True
        elif armType == ArmType.KHI_RS007N_URDF or armType == ArmType.KHI_RS007L_URDF:
            self.rotAx = self.rotAxKHIURDF
            self.isURDF = True
        else:
            self.rotAx = self.rotAxUR

        current = baseLink
        for i in range(self.nlinks):
            current = current + '/' + self.linkNames[i]
            self.linkPaths[i] = current

        # for i in range(self.nlinks):
        #     self.SetAngleDegrees(i, self.curAng[i], True)

    def move(self):
        self.step += 1 / self.fps
        if self.step > 1:
            self.step = 1

        if self.pose:
            newPose = []
            for i in range(len(self.pose)):
                newPose.append((self.pose[i] - self.lastPose[i]) * self.step + self.lastPose[i])
            self.setPose(newPose)
        else:
            print('No such pose ' + RobotPose[self.sequence[self.pos - 1]])
            self.step = 1  # Move to next pose

        if self.step >= 1:
            self.step = 0
            self.lastPose = self.pose if self.pose is not None else self.lastPose
            # print(RobotPose[self.sequence[pos]])
            self.pose = getPose(self.sequence[self.pos])
            self.pos += 1
            if self.pos >= len(self.sequence):
                self.pos = 0

    async def startAnimating(self):
        self.animating = True
        while self.animating:
            self.move()
            await asyncio.sleep(self.ms / 1000)

    def stopAnimating(self):
        self.animating = False

    def setCurrentPose(self, pose):
        self.currentPose = pose
        print(f"Set current pose: {pose}")

    def setPose(self, pose):
        if not pose or len(pose) > self.nlinks:
            print('Incorrect number of angles in pose ', pose)
            return

        for i in range(len(pose)):
            self.SetAngleDegrees(i, pose[i])

    def SetAngleDegrees(self, jidx, oangle, quiet=True):
        # Debug.Log($"SetAngle {jidx} angle:{oangle}");
        if jidx < 0 or self.nlinks <= jidx:
            print(f"joint index out of range: {jidx} nlinks:{self.nlinks}")
            return

        angle = self.jointSign[jidx] * (oangle - self.jointOrg[jidx])
        # ang = clipJoints ? ClipAng(angle, jointMin[jidx], jointMax[jidx], name, linkName[jidx]) : angle;
        ang = angle
        # brot = self.Quang(self.baseAxisURDF[jidx], self.baseAngURDF[jidx])
        # qrot = self.Quang(self.rotAxKHIURDF[jidx] if self.isURDF else self.rotAx[jidx], ang)
        brot = self.Quang(self.rotAxKHI[jidx], self.baseAngURDF[jidx])
        qrot = self.Quang(self.rotAx[jidx], ang)
        self.curAng[jidx] = oangle
        # localRotation = self.quaternion_multiply(brot, qrot)
        localRotation: Gf.Quatf = brot * qrot
        rot = localRotation if self.isURDF else qrot
        self.setJoint(self.linkPaths[jidx], rot)

        if not quiet:
            print(f"Set LocalRotation jidx:{jidx} ang:{ang} qrot:{qrot}")

    def setJoint(self, joint_path: str, new_orientation: Gf.Quatf):
        context = omni.usd.get_context()
        stage = context.get_stage()
        prim = stage.GetPrimAtPath(joint_path)
        if prim is None:
            print(f"Could not find prim at path {joint_path}")
            return
        op = None
        xform = UsdGeom.Xformable(prim)
        for o in xform.GetOrderedXformOps():
            if o.GetOpName() == "xformOp:orient":
                op = o
                break
        if op is None:
            op = xform.AddOrientOp()
        op.Set(new_orientation)

    def vector_to_quat(self, roll, pitch, yaw) -> Gf.Quatf:
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return Gf.Quatf(w, x, y, z)

    def quaternion_multiply(self, Q0: Gf.Quatf, Q1: Gf.Quatf) -> Gf.Quatf:
        # Extract the values from Q0
        im0 = Q0.GetImaginary()
        w0 = Q0.GetReal()
        x0 = im0[0]
        y0 = im0[1]
        z0 = im0[2]

        # Extract the values from Q1
        im1 = Q1.GetImaginary()
        w1 = Q1.GetReal()
        x1 = im1[0]
        y1 = im1[1]
        z1 = im1[2]

        # Compute the product of the two quaternions, term by term
        Q0Q1_w = w0 * w1 - x0 * x1 - y0 * y1 - z0 * z1
        Q0Q1_x = w0 * x1 + x0 * w1 + y0 * z1 - z0 * y1
        Q0Q1_y = w0 * y1 - x0 * z1 + y0 * w1 + z0 * x1
        Q0Q1_z = w0 * z1 + x0 * y1 - y0 * x1 + z0 * w1

        # Return the final quaternion (q02,q12,q22,q32)
        return Gf.Quatf(Q0Q1_w, Q0Q1_x, Q0Q1_y, Q0Q1_z)

    def Quang(self, rotax, ang) -> Gf.Quatf:
        angle = ang * 3.141592653589793 / 180.0
        rot = Gf.Quatf(0, 0, 0, 0)
        if rotax == RotationalAxis.Zero:
            rot = self.vector_to_quat(0, 0, 0)
        elif rotax == RotationalAxis.XPositive:
            rot = self.vector_to_quat(+angle, 0, 0)
        elif rotax == RotationalAxis.XNegative:
            rot = self.vector_to_quat(-angle, 0, 0)
        elif rotax == RotationalAxis.YPositive:
            rot = self.vector_to_quat(0, +angle, 0)
        elif rotax == RotationalAxis.YNegative:
            rot = self.vector_to_quat(0, -angle, 0)
        elif rotax == RotationalAxis.ZPositive:
            rot = self.vector_to_quat(0, 0, +angle)
        elif rotax == RotationalAxis.ZNegative:
            rot = self.vector_to_quat(0, 0, -angle)

        return rot
