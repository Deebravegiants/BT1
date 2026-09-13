# [H] CVE-2024-0743

## Summary
Severity: High
Advisory: CVE-2024-0743
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-0743
Type: osv

## Details
An unchecked return value in TLS handshake code could have caused a potentially exploitable crash. This vulnerability affects Firefox < 122, Firefox ESR < 115.9, and Thunderbird < 115.9.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00028.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00022.html
- https://www.mozilla.org/security/advisories/mfsa2024-01/
- https://www.mozilla.org/security/advisories/mfsa2024-13/
- https://www.mozilla.org/security/advisories/mfsa2024-14/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1867408
