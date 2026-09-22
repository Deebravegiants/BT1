# [M] CVE-2025-8027

## Summary
Severity: Medium
Advisory: CVE-2025-8027
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-8027
Type: osv

## Details
On 64-bit platforms IonMonkey-JIT only wrote 32 bits of the 64-bit return value space on the stack. Baseline-JIT, however, read the entire 64 bits. This vulnerability affects Firefox < 141, Firefox ESR < 115.26, Firefox ESR < 128.13, Firefox ESR < 140.1, Thunderbird < 141, Thunderbird < 128.13, and Thunderbird < 140.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00016.html
- https://www.mozilla.org/security/advisories/mfsa2025-58/
- https://www.mozilla.org/security/advisories/mfsa2025-59/
- https://www.mozilla.org/security/advisories/mfsa2025-62/
- https://www.mozilla.org/security/advisories/mfsa2025-63/
- https://www.mozilla.org/security/advisories/mfsa2025-56/
- https://www.mozilla.org/security/advisories/mfsa2025-57/
- https://www.mozilla.org/security/advisories/mfsa2025-61/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1968423
