# [M] CVE-2019-9456

## Summary
Severity: Medium
Advisory: CVE-2019-9456
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9456
Type: osv

## Details
In the Android kernel in Pixel C USB monitor driver there is a possible OOB write due to a missing bounds check. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://source.android.com/security/bulletin/pixel/2019-09-01
