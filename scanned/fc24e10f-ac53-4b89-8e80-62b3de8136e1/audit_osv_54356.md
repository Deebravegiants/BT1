# [C] CVE-2023-5176

## Summary
Severity: Critical
Advisory: CVE-2023-5176
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-5176
Type: osv

## Details
Memory safety bugs present in Firefox 117, Firefox ESR 115.2, and Thunderbird 115.2. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 118, Firefox ESR < 115.3, and Thunderbird < 115.3.

## References
- https://www.debian.org/security/2023/dsa-5513
- https://www.mozilla.org/security/advisories/mfsa2023-41/
- https://www.mozilla.org/security/advisories/mfsa2023-42/
- https://www.mozilla.org/security/advisories/mfsa2023-43/
- https://lists.debian.org/debian-lts-announce/2023/09/msg00034.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00015.html
- https://www.debian.org/security/2023/dsa-5506
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1836353%2C1842674%2C1843824%2C1843962%2C1848890%2C1850180%2C1850983%2C1851195
