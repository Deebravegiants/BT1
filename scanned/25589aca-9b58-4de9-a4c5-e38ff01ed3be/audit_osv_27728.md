# [H] CVE-2024-25199

## Summary
Severity: High
Advisory: CVE-2024-25199
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-25199
Type: osv

## Details
Inappropriate pointer order of map_sub_ and map_free(map_) (amcl_node.cpp) in Open Robotics Robotic Operating Sytstem 2 (ROS2) and Nav2 humble versions leads to a use-after-free.

## References
- https://github.com/ros-planning/navigation2/blob/main/nav2_amcl/src/amcl_node.cpp#L331-L344
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25199.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25199
- https://github.com/ros-planning/navigation2/pull/4078
- https://github.com/ros-planning/navigation2/pull/4079
