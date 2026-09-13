# [C] CVE-2024-9402

## Summary
Severity: Critical
Advisory: CVE-2024-9402
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-01
Source: https://osv.dev/vulnerability/CVE-2024-9402
Type: osv

## Details
Memory safety bugs present in Firefox 130, Firefox ESR 128.2, and Thunderbird 128.2. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 131, Firefox ESR < 128.3, Thunderbird < 128.3, and Thunderbird < 131.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-47/
- https://www.mozilla.org/security/advisories/mfsa2024-49/
- https://www.mozilla.org/security/advisories/mfsa2024-50/
- https://www.mozilla.org/security/advisories/mfsa2024-46/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1872744%2C1897792%2C1911317%2C1913445%2C1914106%2C1914475%2C1914963%2C1915008%2C1916476
