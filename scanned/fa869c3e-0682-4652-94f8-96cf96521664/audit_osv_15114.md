# [C] CVE-2019-13566

## Summary
Severity: Critical
Advisory: CVE-2019-13566
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-22
Source: https://osv.dev/vulnerability/CVE-2019-13566
Type: osv

## Details
An issue was discovered in the ROS communications-related packages (aka ros_comm or ros-melodic-ros-comm) through 1.14.3. A buffer overflow allows attackers to cause a denial of service and possibly execute arbitrary code via an IP address with a long hostname.

## References
- https://github.com/ros/ros_comm/issues/1752
- https://github.com/ros/ros_comm/issues/1735
- https://github.com/ros/ros_comm/pull/1771
