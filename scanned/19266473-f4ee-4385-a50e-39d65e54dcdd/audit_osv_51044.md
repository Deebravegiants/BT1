# [M] CVE-2021-0342

## Summary
Severity: Medium
Advisory: CVE-2021-0342
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-11
Source: https://osv.dev/vulnerability/CVE-2021-0342
Type: osv

## Details
In tun_get_user of tun.c, there is possible memory corruption due to a use after free. This could lead to local escalation of privilege with System execution privileges required. User interaction is not required for exploitation. Product: Android; Versions: Android kernel; Android ID: A-146554327.

## References
- https://source.android.com/security/bulletin/pixel/2021-01-01
- https://source.android.com/security/bulletin/pixel/2021-01-01
