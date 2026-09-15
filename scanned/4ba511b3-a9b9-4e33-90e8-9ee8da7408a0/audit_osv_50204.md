# [H] CVE-2019-9458

## Summary
Severity: High
Advisory: CVE-2019-9458
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9458
Type: osv

## Details
In the Android kernel in the video driver there is a use after free due to a race condition. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00035.html
- https://source.android.com/security/bulletin/pixel/2019-09-01
