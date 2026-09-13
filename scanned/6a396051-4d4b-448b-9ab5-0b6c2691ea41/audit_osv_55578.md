# [C] CVE-2025-9179

## Summary
Severity: Critical
Advisory: CVE-2025-9179
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-9179
Type: osv

## Details
An attacker was able to perform memory corruption in the GMP process which processes encrypted media. This process is also heavily sandboxed, but represents slightly different privileges from the content process. This vulnerability affects Firefox < 142, Firefox ESR < 115.27, Firefox ESR < 128.14, Firefox ESR < 140.2, Thunderbird < 142, Thunderbird < 128.14, and Thunderbird < 140.2.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00018.html
- https://lists.debian.org/debian-lts-announce/2025/08/msg00016.html
- https://www.mozilla.org/security/advisories/mfsa2025-70/
- https://www.mozilla.org/security/advisories/mfsa2025-72/
- https://www.mozilla.org/security/advisories/mfsa2025-64/
- https://www.mozilla.org/security/advisories/mfsa2025-66/
- https://www.mozilla.org/security/advisories/mfsa2025-71/
- https://www.mozilla.org/security/advisories/mfsa2025-65/
- https://www.mozilla.org/security/advisories/mfsa2025-67/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1979527
