# [M] CVE-2023-6205

## Summary
Severity: Medium
Advisory: CVE-2023-6205
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-6205
Type: osv

## Details
It was possible to cause the use of a MessagePort after it had already been freed, which could potentially have led to an exploitable crash. This vulnerability affects Firefox < 120, Firefox ESR < 115.5.0, and Thunderbird < 115.5.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00030.html
- https://www.debian.org/security/2023/dsa-5561
- https://www.mozilla.org/security/advisories/mfsa2023-49/
- https://www.mozilla.org/security/advisories/mfsa2023-50/
- https://www.mozilla.org/security/advisories/mfsa2023-52/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1854076
- https://lists.debian.org/debian-lts-announce/2023/11/msg00017.html
