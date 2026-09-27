# [M] CVE-2024-2611

## Summary
Severity: Medium
Advisory: CVE-2024-2611
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/CVE-2024-2611
Type: osv

## Details
A missing delay on when pointer lock was used could have allowed a malicious page to trick a user into granting permissions. This vulnerability affects Firefox < 124, Firefox ESR < 115.9, and Thunderbird < 115.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-12/
- https://www.mozilla.org/security/advisories/mfsa2024-13/
- https://www.mozilla.org/security/advisories/mfsa2024-14/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1876675
- https://lists.debian.org/debian-lts-announce/2024/03/msg00022.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00028.html
