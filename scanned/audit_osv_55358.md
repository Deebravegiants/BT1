# [H] CVE-2025-3753

## Summary
Severity: High
Advisory: CVE-2025-3753
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-3753
Type: osv

## Details
A code execution vulnerability has been identified in the Robot Operating System (ROS) 'rosbag' tool, affecting ROS distributions Noetic Ninjemys and earlier. The vulnerability arises from the use of the eval() function to process unsanitized, user-supplied input in the 'rosbag filter' command. This flaw enables attackers to craft and execute arbitrary Python code.

## References
- https://www.ros.org/blog/noetic-eol/
