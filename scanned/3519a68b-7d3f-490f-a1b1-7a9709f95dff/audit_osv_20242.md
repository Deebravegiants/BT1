# [C] CVE-2021-32563

## Summary
Severity: Critical
Advisory: CVE-2021-32563
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-11
Source: https://osv.dev/vulnerability/CVE-2021-32563
Type: osv

## Details
An issue was discovered in Thunar before 4.16.7 and 4.17.x before 4.17.2. When called with a regular file as a command-line argument, it delegates to a different program (based on the file type) without user confirmation. This could be used to achieve code execution.

## References
- http://www.openwall.com/lists/oss-security/2021/05/11/3
- http://www.openwall.com/lists/oss-security/2023/01/05/1
- http://www.openwall.com/lists/oss-security/2023/01/05/2
- https://gitlab.xfce.org/xfce/thunar/-/tags
- https://www.openwall.com/lists/oss-security/2021/05/09/2
- https://gitlab.xfce.org/xfce/thunar/-/commit/1b85b96ebf7cb9bf6a3ddf1acee7643643fdf92d
- https://gitlab.xfce.org/xfce/thunar/-/commit/3b54d9d7dbd7fd16235e2141c43a7f18718f5664
- https://gitlab.xfce.org/xfce/thunar/-/commit/9165a61f95e43cc0b5abf9b98eee2818a0191e0b
