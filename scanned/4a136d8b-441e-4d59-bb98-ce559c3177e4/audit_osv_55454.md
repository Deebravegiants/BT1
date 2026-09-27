# [M] CVE-2025-5264

## Summary
Severity: Medium
Advisory: CVE-2025-5264
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-5264
Type: osv

## Details
Due to insufficient escaping of the newline character in the “Copy as cURL” feature, an attacker could trick a user into using this command, potentially leading to local code execution on the user's system. This vulnerability affects Firefox < 139, Firefox ESR < 115.24, Firefox ESR < 128.11, Thunderbird < 139, and Thunderbird < 128.11.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00043.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00046.html
- https://www.mozilla.org/security/advisories/mfsa2025-43/
- https://www.mozilla.org/security/advisories/mfsa2025-44/
- https://www.mozilla.org/security/advisories/mfsa2025-45/
- https://www.mozilla.org/security/advisories/mfsa2025-46/
- https://www.mozilla.org/security/advisories/mfsa2025-42/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1950001
