# [M] CVE-2024-4769

## Summary
Severity: Medium
Advisory: CVE-2024-4769
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/CVE-2024-4769
Type: osv

## Details
When importing resources using Web Workers, error messages would distinguish the difference between `application/javascript` responses and non-script responses.  This could have been abused to learn information cross-origin. This vulnerability affects Firefox < 126, Firefox ESR < 115.11, and Thunderbird < 115.11.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-21/
- https://www.mozilla.org/security/advisories/mfsa2024-22/
- https://www.mozilla.org/security/advisories/mfsa2024-23/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1886108
- https://lists.debian.org/debian-lts-announce/2024/05/msg00010.html
- https://lists.debian.org/debian-lts-announce/2024/05/msg00012.html
