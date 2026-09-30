# [M] CVE-2025-8033

## Summary
Severity: Medium
Advisory: CVE-2025-8033
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-8033
Type: osv

## Details
The JavaScript engine did not handle closed generators correctly and it was possible to resume them leading to a nullptr deref. This vulnerability affects Firefox < 141, Firefox ESR < 115.26, Firefox ESR < 128.13, Firefox ESR < 140.1, Thunderbird < 141, Thunderbird < 128.13, and Thunderbird < 140.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00016.html
- https://www.mozilla.org/security/advisories/mfsa2025-56/
- https://www.mozilla.org/security/advisories/mfsa2025-57/
- https://www.mozilla.org/security/advisories/mfsa2025-61/
- https://www.mozilla.org/security/advisories/mfsa2025-58/
- https://www.mozilla.org/security/advisories/mfsa2025-59/
- https://www.mozilla.org/security/advisories/mfsa2025-62/
- https://www.mozilla.org/security/advisories/mfsa2025-63/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1973990
