# [C] CVE-2024-39780

## Summary
Severity: Critical
Advisory: CVE-2024-39780
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2024-39780
Type: osv

## Details
A YAML deserialization vulnerability was found in the Robot Operating System (ROS) 'dynparam', a command-line tool for getting, setting, and deleting parameters of a dynamically configurable node, affecting ROS distributions Noetic and earlier. The issue is caused by the use of the yaml.load() function in the 'set' and 'get' verbs, and allows for the creation of arbitrary Python objects. Through this flaw, a local or remote user can craft and execute arbitrary Python code.

## References
- https://github.com/ros/dynamic_reconfigure/pull/202
