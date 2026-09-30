# [H] CVE-2024-1553

## Summary
Severity: High
Advisory: CVE-2024-1553
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-1553
Type: osv

## Details
Memory safety bugs present in Firefox 122, Firefox ESR 115.7, and Thunderbird 115.7. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 123, Firefox ESR < 115.8, and Thunderbird < 115.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-05/
- https://www.mozilla.org/security/advisories/mfsa2024-06/
- https://www.mozilla.org/security/advisories/mfsa2024-07/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1855686%2C1867982%2C1871498%2C1872296%2C1873521%2C1873577%2C1873597%2C1873866%2C1874080%2C1874740%2C1875795%2C1875906%2C1876425%2C1878211%2C1878286
- https://lists.debian.org/debian-lts-announce/2024/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00001.html
