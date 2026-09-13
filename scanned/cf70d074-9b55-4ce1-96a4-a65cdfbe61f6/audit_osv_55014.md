# [C] CVE-2024-8387

## Summary
Severity: Critical
Advisory: CVE-2024-8387
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-8387
Type: osv

## Details
Memory safety bugs present in Firefox 129, Firefox ESR 128.1, and Thunderbird 128.1. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 130, Firefox ESR < 128.2, and Thunderbird < 128.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-39/
- https://www.mozilla.org/security/advisories/mfsa2024-40/
- https://www.mozilla.org/security/advisories/mfsa2024-43/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1857607%2C1911858%2C1914009
