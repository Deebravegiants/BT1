# [M] CVE-2024-0747

## Summary
Severity: Medium
Advisory: CVE-2024-0747
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-0747
Type: osv

## Details
When a parent page loaded a child in an iframe with `unsafe-inline`, the parent Content Security Policy could have overridden the child Content Security Policy. This vulnerability affects Firefox < 122, Firefox ESR < 115.7, and Thunderbird < 115.7.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00022.html
- https://www.mozilla.org/security/advisories/mfsa2024-01/
- https://www.mozilla.org/security/advisories/mfsa2024-02/
- https://www.mozilla.org/security/advisories/mfsa2024-04/
- https://lists.debian.org/debian-lts-announce/2024/01/msg00015.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1764343
