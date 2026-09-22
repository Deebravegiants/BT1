# [H] CVE-2024-39289

## Summary
Severity: High
Advisory: CVE-2024-39289
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2024-39289
Type: osv

## Details
A code execution vulnerability has been discovered in the Robot Operating System (ROS) 'rosparam' tool, affecting ROS distributions Noetic Ninjemys and earlier. The vulnerability stems from the use of the eval() function to process unsanitized, user-supplied parameter values via special converters for angle representations in radians. This flaw allowed attackers to craft and execute arbitrary Python code.

## References
- https://www.ros.org/blog/noetic-eol/
