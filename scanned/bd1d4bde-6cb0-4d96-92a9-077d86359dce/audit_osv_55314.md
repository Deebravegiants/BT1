# [H] CVE-2025-3030

## Summary
Severity: High
Advisory: CVE-2025-3030
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-3030
Type: osv

## Details
Memory safety bugs present in Firefox 136, Thunderbird 136, Firefox ESR 128.8, and Thunderbird 128.8. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 137, Firefox ESR < 128.9, Thunderbird < 137, and Thunderbird < 128.9.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00005.html
- https://www.mozilla.org/security/advisories/mfsa2025-24/
- https://www.mozilla.org/security/advisories/mfsa2025-20/
- https://www.mozilla.org/security/advisories/mfsa2025-22/
- https://www.mozilla.org/security/advisories/mfsa2025-23/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1850615%2C1932468%2C1942551%2C1951017%2C1951494
