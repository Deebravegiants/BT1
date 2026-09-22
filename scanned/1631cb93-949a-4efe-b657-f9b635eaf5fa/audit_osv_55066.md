# [M] CVE-2025-0243

## Summary
Severity: Medium
Advisory: CVE-2025-0243
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-0243
Type: osv

## Details
Memory safety bugs present in Firefox 133, Thunderbird 133, Firefox ESR 128.5, and Thunderbird 128.5. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 134, Firefox ESR < 128.6, Thunderbird < 134, and Thunderbird < 128.6.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00004.html
- https://www.mozilla.org/security/advisories/mfsa2025-01/
- https://www.mozilla.org/security/advisories/mfsa2025-02/
- https://www.mozilla.org/security/advisories/mfsa2025-04/
- https://www.mozilla.org/security/advisories/mfsa2025-05/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1827142%2C1932783
