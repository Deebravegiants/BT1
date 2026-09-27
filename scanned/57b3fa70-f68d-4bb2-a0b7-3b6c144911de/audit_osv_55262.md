# [M] CVE-2025-1938

## Summary
Severity: Medium
Advisory: CVE-2025-1938
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-1938
Type: osv

## Details
Memory safety bugs present in Firefox 135, Thunderbird 135, Firefox ESR 128.7, and Thunderbird 128.7. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 136, Firefox ESR < 128.8, Thunderbird < 136, and Thunderbird < 128.8.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00006.html
- https://www.mozilla.org/security/advisories/mfsa2025-14/
- https://www.mozilla.org/security/advisories/mfsa2025-16/
- https://www.mozilla.org/security/advisories/mfsa2025-17/
- https://www.mozilla.org/security/advisories/mfsa2025-18/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1922889%2C1935004%2C1943586%2C1943912%2C1948111
