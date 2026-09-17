# [H] CVE-2025-1012

## Summary
Severity: High
Advisory: CVE-2025-1012
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-04
Source: https://osv.dev/vulnerability/CVE-2025-1012
Type: osv

## Details
A race during concurrent delazification could have led to a use-after-free. This vulnerability affects Firefox < 135, Firefox ESR < 115.20, Firefox ESR < 128.7, Thunderbird < 128.7, and Thunderbird < 135.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00005.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00006.html
- https://www.mozilla.org/security/advisories/mfsa2025-07/
- https://www.mozilla.org/security/advisories/mfsa2025-08/
- https://www.mozilla.org/security/advisories/mfsa2025-09/
- https://www.mozilla.org/security/advisories/mfsa2025-10/
- https://www.mozilla.org/security/advisories/mfsa2025-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1939710
