# [C] CVE-2024-25198

## Summary
Severity: Critical
Advisory: CVE-2024-25198
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-25198
Type: osv

## Details
Inappropriate pointer order of laser_scan_filter_.reset() and tf_listener_.reset() (amcl_node.cpp) in Open Robotics Robotic Operating Sytstem 2 (ROS2) and Nav2 humble versions leads to a use-after-free.

## References
- https://github.com/ros-planning/navigation2/blob/main/nav2_amcl/src/amcl_node.cpp#L331-L344
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25198.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25198
- https://github.com/ros-planning/navigation2/pull/4068
- https://github.com/ros-planning/navigation2/pull/4070
