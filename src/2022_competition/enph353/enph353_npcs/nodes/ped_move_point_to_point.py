#!/usr/bin/env python3
import math
import numpy as np
import random
import rospy

from geometry_msgs.msg import Twist, PoseStamped, Pose
from tf.transformations import euler_from_quaternion
from gazebo_msgs.msg import ModelStates
class CrosswalkController():

    def __init__(self):
        self.pose_sub = rospy.Subscriber('/gazebo/model_states', ModelStates, self.pose_feedback_callback, queue_size=1)
        self.vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1, latch=False)
        self.pose = None
        self.pose_a = Pose()
        self.pose_b = Pose()
        self.heading_deadband = 0.2
        self.position_deadband = 0.015
        self.name = rospy.get_param('~name')

        self.pose_a.position.x = rospy.get_param('~pose_a_x')
        self.pose_a.position.y = rospy.get_param('~pose_a_y')
        self.pose_b.position.x = rospy.get_param('~pose_b_x')
        self.pose_b.position.y = rospy.get_param('~pose_b_y')
        self.pose_goal_buffer = []
        self.pose_goal_buffer.append(self.pose_b)
        self.pose_goal_buffer.append(self.pose_a)
        self.pose_goal = self.pose_goal_buffer[0]

        self.max_angular_vel = 2
        self.max_linear_vel = random.uniform(0.5, 1)
        self.WAIT_TIME_s = random.uniform(0.5, 2)
        self.at_rest = False
        self.last_reached_dest_time = rospy.Time.now()

    def pose_feedback_callback(self, msg):
        if(msg is not None):
            if(self.name in msg.name):
                index = msg.name.index(self.name)
                self.pose = msg.pose[index]

                if self.pose is not None and self.pose_goal is not None:
                    current_rpy = euler_from_quaternion((self.pose.orientation.x,self.pose.orientation.y,self.pose.orientation.z,self.pose.orientation.w))
                    dest_rpy = euler_from_quaternion((self.pose_goal.orientation.x, self.pose_goal.orientation.y, self.pose_goal.orientation.z, self.pose_goal.orientation.w))
                    dx = self.pose_goal.position.x - self.pose.position.x
                    dy = self.pose_goal.position.y - self.pose.position.y
                    heading = math.atan2(dy, dx)
                    angle = current_rpy[2]-heading
                    while angle >= math.pi:
                        angle = angle - 2*math.pi
                    while angle <= -math.pi:
                        angle = angle + 2*math.pi
                    dist = math.hypot(dy,dx)
                    cmd_vel = Twist()
                    cmd_vel.angular.z = 0
                    cmd_vel.linear.x = 0
                    # Rotate to the direct goal heading
                    if abs(angle) > self.heading_deadband and dist > self.position_deadband and not self.at_rest:
                        # print("Aligning with heading")
                        if angle > self.heading_deadband:
                            cmd_vel.angular.z = -self.max_angular_vel
                        elif angle < -self.heading_deadband:
                            cmd_vel.angular.z = self.max_angular_vel
                    # Drive forwards to goal position
                    elif dist > self.position_deadband:
                        # print("Moving to destination position",dist)
                        cmd_vel.linear.x = self.max_linear_vel 
                    # Rotate to align with goal orientation
                    # elif dist < self.position_deadband and abs(current_rpy[2] - dest_rpy[2]) < self.orientation_deadband and not self.at_rest:
                    #     print("Aligning with desintation orientation")
                    #     if current_rpy[2] - dest_rpy[2] > 0:
                    #         cmd_vel.angular.z = -self.max_angular_vel
                    #     else:
                    #         cmd_vel.angular.z = self.max_angular_vel
                    else:
                        # print("Reached goal")
                        if not self.at_rest:
                            self.last_reached_dest_time = rospy.Time.now()
                            self.at_rest = True
                            self.WAIT_TIME_s = random.uniform(1, 2.5)
                            self.max_linear_vel = random.uniform(0.5, 1)
                        elif rospy.Time.now() - self.last_reached_dest_time > rospy.Duration(self.WAIT_TIME_s) and self.at_rest:
                            self.at_rest = False
                            self.pose_goal_buffer[0], self.pose_goal_buffer[-1] = self.pose_goal_buffer[-1], self.pose_goal_buffer[0]
                            self.pose_goal = self.pose_goal_buffer[0]

                    self.vel_pub.publish(cmd_vel)

if __name__ == '__main__':
    rospy.init_node('drive_point_to_point')
    cw = CrosswalkController()
    try:
        rospy.spin()
    except rospy.ROSInterruptException:
        pass