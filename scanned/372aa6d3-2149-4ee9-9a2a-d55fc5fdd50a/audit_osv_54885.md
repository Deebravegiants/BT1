# [M] CVE-2024-5693

## Summary
Severity: Medium
Advisory: CVE-2024-5693
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/CVE-2024-5693
Type: osv

## Details
Offscreen Canvas did not properly track cross-origin tainting, which could be used to access image data from another site in violation of same-origin policy. This vulnerability affects Firefox < 127, Firefox ESR < 115.12, and Thunderbird < 115.12.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00010.html
- https://www.mozilla.org/security/advisories/mfsa2024-25/
- https://www.mozilla.org/security/advisories/mfsa2024-26/
- https://www.mozilla.org/security/advisories/mfsa2024-28/
- https://lists.debian.org/debian-lts-announce/2024/06/msg00000.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1891319
