# [H] CVE-2024-5700

## Summary
Severity: High
Advisory: CVE-2024-5700
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/CVE-2024-5700
Type: osv

## Details
Memory safety bugs present in Firefox 126, Firefox ESR 115.11, and Thunderbird 115.11. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 127, Firefox ESR < 115.12, and Thunderbird < 115.12.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-25/
- https://www.mozilla.org/security/advisories/mfsa2024-26/
- https://www.mozilla.org/security/advisories/mfsa2024-28/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1862809%2C1889355%2C1893388%2C1895123
- https://lists.debian.org/debian-lts-announce/2024/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00010.html
