# [M] CVE-2019-19625

## Summary
Severity: Medium
Advisory: CVE-2019-19625
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-12-06
Source: https://osv.dev/vulnerability/CVE-2019-19625
Type: osv

## Details
SROS 2 0.8.1 (which provides the tools that generate and distribute keys for Robot Operating System 2 and uses the underlying security plugins of DDS from ROS 2) leaks node information due to a leaky default configuration as indicated in the policy/defaults/dds/governance.xml document.

## References
- https://github.com/ros2/sros2/pull/171
- https://github.com/aliasrobotics/RVD/issues/922
