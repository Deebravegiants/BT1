# [H] CVE-2023-21255

## Summary
Severity: High
Advisory: CVE-2023-21255
Aliases: A-275041864, ASB-A-275041864
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/CVE-2023-21255
Type: osv

## Details
In multiple functions of binder.c, there is a possible memory corruption due to a use after free. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20240119-0010/
- https://www.debian.org/security/2023/dsa-5480
- https://android.googlesource.com/kernel/common/+/1ca1130ec62d
- https://source.android.com/security/bulletin/2023-07-01
