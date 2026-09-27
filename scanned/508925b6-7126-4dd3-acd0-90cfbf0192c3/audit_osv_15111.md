# [H] CVE-2019-13465

## Summary
Severity: High
Advisory: CVE-2019-13465
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-13465
Type: osv

## Details
An issue was discovered in the ROS communications-related packages (aka ros_comm or ros-melodic-ros-comm) through 1.14.3. ROS_ASSERT_MSG only works when ROS_ASSERT_ENABLED is defined. This leads to a problem in the remove() function in clients/roscpp/src/libros/spinner.cpp. When ROS_ASSERT_ENABLED is not defined, the iterator loop will run out of the scope of the array, and cause denial of service for other components (that depend on the communication-related functions of this package). NOTE: The reporter of this issue now believes it was a false alarm.

## References
- https://github.com/ros/ros_comm/issues/1748
