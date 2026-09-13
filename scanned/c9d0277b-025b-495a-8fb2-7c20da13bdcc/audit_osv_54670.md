# [M] CVE-2024-2609

## Summary
Severity: Medium
Advisory: CVE-2024-2609
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/CVE-2024-2609
Type: osv

## Details
The permission prompt input delay could expire while the window is not in focus. This makes it vulnerable to clickjacking by malicious websites. This vulnerability affects Firefox < 124, Firefox ESR < 115.10, and Thunderbird < 115.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-12/
- https://www.mozilla.org/security/advisories/mfsa2024-19/
- https://www.mozilla.org/security/advisories/mfsa2024-20/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1866100
- https://lists.debian.org/debian-lts-announce/2024/04/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/04/msg00013.html
