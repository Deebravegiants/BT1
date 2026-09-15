# [H] CVE-2025-4091

## Summary
Severity: High
Advisory: CVE-2025-4091
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2025-4091
Type: osv

## Details
Memory safety bugs present in Firefox 137, Thunderbird 137, Firefox ESR 128.9, and Thunderbird 128.9. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 138, Firefox ESR < 128.10, Thunderbird < 138, and Thunderbird < 128.10.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00024.html
- https://www.mozilla.org/security/advisories/mfsa2025-29/
- https://www.mozilla.org/security/advisories/mfsa2025-31/
- https://www.mozilla.org/security/advisories/mfsa2025-32/
- https://www.mozilla.org/security/advisories/mfsa2025-28/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1951161%2C1952105
