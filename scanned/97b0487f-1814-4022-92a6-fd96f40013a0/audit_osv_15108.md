# [C] CVE-2019-13445

## Summary
Severity: Critical
Advisory: CVE-2019-13445
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-13445
Type: osv

## Details
An issue was discovered in the ROS communications-related packages (aka ros_comm or ros-melodic-ros-comm) through 1.14.3. parseOptions() in tools/rosbag/src/record.cpp has an integer overflow when a crafted split option can be entered on the command line.

## References
- https://github.com/ros/ros_comm/pull/1741
- https://github.com/ros/ros_comm/blob/melodic-devel/tools/rosbag/src/record.cpp#L129
- https://github.com/ros/ros_comm/issues/1738
