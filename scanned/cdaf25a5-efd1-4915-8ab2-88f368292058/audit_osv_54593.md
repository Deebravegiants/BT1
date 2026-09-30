# [M] CVE-2024-1549

## Summary
Severity: Medium
Advisory: CVE-2024-1549
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-1549
Type: osv

## Details
If a website set a large custom cursor, portions of the cursor could have overlapped with the permission dialog, potentially resulting in user confusion and unexpected granted permissions. This vulnerability affects Firefox < 123, Firefox ESR < 115.8, and Thunderbird < 115.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-05/
- https://www.mozilla.org/security/advisories/mfsa2024-06/
- https://www.mozilla.org/security/advisories/mfsa2024-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1833814
- https://lists.debian.org/debian-lts-announce/2024/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00001.html
