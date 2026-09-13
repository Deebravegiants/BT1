# [H] CVE-2019-2182

## Summary
Severity: High
Advisory: CVE-2019-2182
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-2182
Type: osv

## Details
In the Android kernel in the kernel MMU code there is a possible execution path leaving some kernel text and rodata pages writable. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.

## References
- https://source.android.com/security/bulletin/pixel/2019-09-01
- https://www.debian.org/security/2020/dsa-4698
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
