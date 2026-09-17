# [H] CVE-2025-1014

## Summary
Severity: High
Advisory: CVE-2025-1014
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-04
Source: https://osv.dev/vulnerability/CVE-2025-1014
Type: osv

## Details
Certificate length was not properly checked when added to a certificate store. In practice only trusted data was processed. This vulnerability affects Firefox < 135, Firefox ESR < 128.7, Thunderbird < 128.7, and Thunderbird < 135.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00006.html
- https://www.mozilla.org/security/advisories/mfsa2025-10/
- https://www.mozilla.org/security/advisories/mfsa2025-11/
- https://www.mozilla.org/security/advisories/mfsa2025-07/
- https://www.mozilla.org/security/advisories/mfsa2025-09/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1940804
