# [H] CVE-2019-15901

## Summary
Severity: High
Advisory: CVE-2019-15901
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-18
Source: https://osv.dev/vulnerability/CVE-2019-15901
Type: osv

## Details
An issue was discovered in slicer69 doas before 6.2 on certain platforms other than OpenBSD. A setusercontext(3) call with flags to change the UID, primary GID, and secondary GIDs was replaced (on certain platforms: Linux and possibly NetBSD) with a single setuid(2) call. This resulted in neither changing the group id nor initializing secondary group ids.

## References
- https://github.com/slicer69/doas/commit/6cf0236184ff6304bf5e267ccf7ef02874069697
- https://github.com/slicer69/doas/compare/6.1p1...6.2
- https://github.com/slicer69/doas/pull/23
