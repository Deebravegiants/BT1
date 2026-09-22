# [H] CVE-2025-5268

## Summary
Severity: High
Advisory: CVE-2025-5268
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-5268
Type: osv

## Details
Memory safety bugs present in Firefox 138, Thunderbird 138, Firefox ESR 128.10, and Thunderbird 128.10. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 139, Firefox ESR < 128.11, Thunderbird < 139, and Thunderbird < 128.11.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00043.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00046.html
- https://www.mozilla.org/security/advisories/mfsa2025-42/
- https://www.mozilla.org/security/advisories/mfsa2025-44/
- https://www.mozilla.org/security/advisories/mfsa2025-45/
- https://www.mozilla.org/security/advisories/mfsa2025-46/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1950136%2C1958121%2C1960499%2C1962634
