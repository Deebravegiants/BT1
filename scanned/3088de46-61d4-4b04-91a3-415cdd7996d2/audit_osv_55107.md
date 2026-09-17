# [C] CVE-2025-1017

## Summary
Severity: Critical
Advisory: CVE-2025-1017
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-04
Source: https://osv.dev/vulnerability/CVE-2025-1017
Type: osv

## Details
Memory safety bugs present in Firefox 134, Thunderbird 134, Firefox ESR 128.6, and Thunderbird 128.6. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 135, Firefox ESR < 128.7, Thunderbird < 128.7, and Thunderbird < 135.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00006.html
- https://www.mozilla.org/security/advisories/mfsa2025-07/
- https://www.mozilla.org/security/advisories/mfsa2025-09/
- https://www.mozilla.org/security/advisories/mfsa2025-10/
- https://www.mozilla.org/security/advisories/mfsa2025-11/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1926256%2C1935984%2C1935471
