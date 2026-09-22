# [H] CVE-2024-41148

## Summary
Severity: High
Advisory: CVE-2024-41148
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2024-41148
Type: osv

## Details
A code injection vulnerability has been discovered in the Robot Operating System (ROS) 'rostopic' command-line tool, affecting ROS distributions Noetic Ninjemys and earlier. The vulnerability lies in the 'hz' verb, which reports the publishing rate of a topic and accepts a user-provided Python expression via the --filter option. This input is passed directly to the eval() function without sanitization, allowing a local user to craft and execute arbitrary code.

## References
- https://www.ros.org/blog/noetic-eol/
