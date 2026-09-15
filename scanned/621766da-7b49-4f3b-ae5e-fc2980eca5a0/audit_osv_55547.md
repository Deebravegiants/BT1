# [C] CVE-2025-8028

## Summary
Severity: Critical
Advisory: CVE-2025-8028
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-8028
Type: osv

## Details
On arm64, a WASM `br_table` instruction with a lot of entries could lead to the label being too far from the instruction causing truncation and incorrect computation of the branch address. This vulnerability affects Firefox < 141, Firefox ESR < 115.26, Firefox ESR < 128.13, Firefox ESR < 140.1, Thunderbird < 141, Thunderbird < 128.13, and Thunderbird < 140.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00016.html
- https://www.mozilla.org/security/advisories/mfsa2025-56/
- https://www.mozilla.org/security/advisories/mfsa2025-57/
- https://www.mozilla.org/security/advisories/mfsa2025-58/
- https://www.mozilla.org/security/advisories/mfsa2025-61/
- https://www.mozilla.org/security/advisories/mfsa2025-59/
- https://www.mozilla.org/security/advisories/mfsa2025-62/
- https://www.mozilla.org/security/advisories/mfsa2025-63/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1971581
