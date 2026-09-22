# [H] CVE-2020-10289

## Summary
Severity: High
Advisory: CVE-2020-10289
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-20
Source: https://osv.dev/vulnerability/CVE-2020-10289
Type: osv

## Details
Use of unsafe yaml load. Allows instantiation of arbitrary objects. The flaw itself is caused by an unsafe parsing of YAML values which happens whenever an action message is processed to be sent, and allows for the creation of Python objects. Through this flaw in the ROS core package of actionlib, an attacker with local or remote access can make the ROS Master, execute arbitrary code in Python form. Consider yaml.safe_load() instead. Located first in actionlib/tools/library.py:132. See links for more info on the bug.

## References
- https://github.com/ros/actionlib/pull/171
- https://github.com/ros/actionlib/pull/171
