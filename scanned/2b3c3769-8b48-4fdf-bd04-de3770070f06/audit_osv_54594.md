# [M] CVE-2024-1550

## Summary
Severity: Medium
Advisory: CVE-2024-1550
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-1550
Type: osv

## Details
A malicious website could have used a combination of exiting fullscreen mode and `requestPointerLock` to cause the user's mouse to be re-positioned unexpectedly, which could have led to user confusion and inadvertently granting permissions they did not intend to grant. This vulnerability affects Firefox < 123, Firefox ESR < 115.8, and Thunderbird < 115.8.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00001.html
- https://www.mozilla.org/security/advisories/mfsa2024-05/
- https://www.mozilla.org/security/advisories/mfsa2024-06/
- https://www.mozilla.org/security/advisories/mfsa2024-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1860065
- https://lists.debian.org/debian-lts-announce/2024/03/msg00000.html
