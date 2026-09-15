# [M] CVE-2023-6204

## Summary
Severity: Medium
Advisory: CVE-2023-6204
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-6204
Type: osv

## Details
On some systems—depending on the graphics settings and drivers—it was possible to force an out-of-bounds read and leak memory data into the images created on the canvas element. This vulnerability affects Firefox < 120, Firefox ESR < 115.5.0, and Thunderbird < 115.5.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00030.html
- https://www.mozilla.org/security/advisories/mfsa2023-49/
- https://www.mozilla.org/security/advisories/mfsa2023-50/
- https://www.mozilla.org/security/advisories/mfsa2023-52/
- https://www.debian.org/security/2023/dsa-5561
- https://bugzilla.mozilla.org/show_bug.cgi?id=1841050
- https://lists.debian.org/debian-lts-announce/2023/11/msg00017.html
