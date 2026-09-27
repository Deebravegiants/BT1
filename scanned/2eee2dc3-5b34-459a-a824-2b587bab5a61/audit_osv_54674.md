# [H] CVE-2024-2614

## Summary
Severity: High
Advisory: CVE-2024-2614
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/CVE-2024-2614
Type: osv

## Details
Memory safety bugs present in Firefox 123, Firefox ESR 115.8, and Thunderbird 115.8. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 124, Firefox ESR < 115.9, and Thunderbird < 115.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-13/
- https://www.mozilla.org/security/advisories/mfsa2024-14/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00022.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00028.html
- https://www.mozilla.org/security/advisories/mfsa2024-12/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1685358%2C1861016%2C1880405%2C1881093
