# [H] CVE-2024-4777

## Summary
Severity: High
Advisory: CVE-2024-4777
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/CVE-2024-4777
Type: osv

## Details
Memory safety bugs present in Firefox 125, Firefox ESR 115.10, and Thunderbird 115.10. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 126, Firefox ESR < 115.11, and Thunderbird < 115.11.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-21/
- https://www.mozilla.org/security/advisories/mfsa2024-22/
- https://www.mozilla.org/security/advisories/mfsa2024-23/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1878199%2C1893340
- https://lists.debian.org/debian-lts-announce/2024/05/msg00010.html
- https://lists.debian.org/debian-lts-announce/2024/05/msg00012.html
