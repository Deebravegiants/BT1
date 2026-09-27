# [H] CVE-2024-6604

## Summary
Severity: High
Advisory: CVE-2024-6604
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-6604
Type: osv

## Details
Memory safety bugs present in Firefox 127, Firefox ESR 115.12, and Thunderbird 115.12. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 128, Firefox ESR < 115.13, Thunderbird < 115.13, and Thunderbird < 128.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-29/
- https://www.mozilla.org/security/advisories/mfsa2024-30/
- https://www.mozilla.org/security/advisories/mfsa2024-31/
- https://www.mozilla.org/security/advisories/mfsa2024-32/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1748105%2C1837550%2C1884266
