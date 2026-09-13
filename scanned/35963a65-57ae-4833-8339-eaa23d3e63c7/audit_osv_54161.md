# [C] CVE-2023-4057

## Summary
Severity: Critical
Advisory: CVE-2023-4057
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-01
Source: https://osv.dev/vulnerability/CVE-2023-4057
Type: osv

## Details
Memory safety bugs present in Firefox 115, Firefox ESR 115.0, and Thunderbird 115.0. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 116, Firefox ESR < 115.1, and Thunderbird < 115.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-29/
- https://www.mozilla.org/security/advisories/mfsa2023-31/
- https://www.mozilla.org/security/advisories/mfsa2023-33/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1841682
