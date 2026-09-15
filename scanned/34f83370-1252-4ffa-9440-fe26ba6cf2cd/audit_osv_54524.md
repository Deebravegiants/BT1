# [H] CVE-2024-0755

## Summary
Severity: High
Advisory: CVE-2024-0755
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-0755
Type: osv

## Details
Memory safety bugs present in Firefox 121, Firefox ESR 115.6, and Thunderbird 115.6. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 122, Firefox ESR < 115.7, and Thunderbird < 115.7.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00015.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00022.html
- https://www.mozilla.org/security/advisories/mfsa2024-01/
- https://www.mozilla.org/security/advisories/mfsa2024-02/
- https://www.mozilla.org/security/advisories/mfsa2024-04/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1868456%2C1871445%2C1873701
