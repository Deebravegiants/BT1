# [M] CVE-2025-5263

## Summary
Severity: Medium
Advisory: CVE-2025-5263
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-5263
Type: osv

## Details
Error handling for script execution was incorrectly isolated from web content, which could have allowed cross-origin leak attacks. This vulnerability affects Firefox < 139, Firefox ESR < 115.24, Firefox ESR < 128.11, Thunderbird < 139, and Thunderbird < 128.11.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00043.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00046.html
- https://www.mozilla.org/security/advisories/mfsa2025-42/
- https://www.mozilla.org/security/advisories/mfsa2025-43/
- https://www.mozilla.org/security/advisories/mfsa2025-44/
- https://www.mozilla.org/security/advisories/mfsa2025-45/
- https://www.mozilla.org/security/advisories/mfsa2025-46/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1960745
