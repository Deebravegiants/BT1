# [C] CVE-2023-5730

## Summary
Severity: Critical
Advisory: CVE-2023-5730
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-5730
Type: osv

## Details
Memory safety bugs present in Firefox 118, Firefox ESR 115.3, and Thunderbird 115.3. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 119, Firefox ESR < 115.4, and Thunderbird < 115.4.1.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00037.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00042.html
- https://www.debian.org/security/2023/dsa-5535
- https://www.debian.org/security/2023/dsa-5538
- https://www.mozilla.org/security/advisories/mfsa2023-45/
- https://www.mozilla.org/security/advisories/mfsa2023-46/
- https://www.mozilla.org/security/advisories/mfsa2023-47/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1836607%2C1840918%2C1848694%2C1848833%2C1850191%2C1850259%2C1852596%2C1853201%2C1854002%2C1855306%2C1855640%2C1856695
