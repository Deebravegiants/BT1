# [C] CVE-2020-27794

## Summary
Severity: Critical
Advisory: CVE-2020-27794
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-08-19
Source: https://osv.dev/vulnerability/CVE-2020-27794
Type: osv

## Details
A double free issue was discovered in radare2 in cmd_info.c:cmd_info(). Successful exploitation could lead to modification of unexpected memory locations and potentially causing a crash.

## References
- https://github.com/radareorg/radare2/commit/cb8b683758edddae2d2f62e8e63a738c39f92683
- https://github.com/radareorg/radare2/issues/16303
