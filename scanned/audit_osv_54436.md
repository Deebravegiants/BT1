# [H] CVE-2023-6212

## Summary
Severity: High
Advisory: CVE-2023-6212
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-6212
Type: osv

## Details
Memory safety bugs present in Firefox 119, Firefox ESR 115.4, and Thunderbird 115.4. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 120, Firefox ESR < 115.5.0, and Thunderbird < 115.5.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00030.html
- https://www.debian.org/security/2023/dsa-5561
- https://www.mozilla.org/security/advisories/mfsa2023-49/
- https://www.mozilla.org/security/advisories/mfsa2023-50/
- https://www.mozilla.org/security/advisories/mfsa2023-52/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1658432%2C1820983%2C1829252%2C1856072%2C1856091%2C1859030%2C1860943%2C1862782
- https://lists.debian.org/debian-lts-announce/2023/11/msg00017.html
