# [M] CVE-2021-0308

## Summary
Severity: Medium
Advisory: CVE-2021-0308
Aliases: A-158063095, ASB-A-158063095
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-11
Source: https://osv.dev/vulnerability/CVE-2021-0308
Type: osv

## Details
In ReadLogicalParts of basicmbr.cc, there is a possible out of bounds write due to a missing bounds check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android; Versions: Android-8.1, Android-9, Android-10, Android-11, Android-8.0; Android ID: A-158063095.

## References
- https://source.android.com/security/bulletin/2021-01-01
- https://lists.debian.org/debian-lts-announce/2021/02/msg00010.html
- https://security.gentoo.org/glsa/202105-03
