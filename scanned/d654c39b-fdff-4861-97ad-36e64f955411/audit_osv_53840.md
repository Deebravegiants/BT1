# [H] CVE-2023-28176

## Summary
Severity: High
Advisory: CVE-2023-28176
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-28176
Type: osv

## Details
Memory safety bugs present in Firefox 110 and Firefox ESR 102.8. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 111, Firefox ESR < 102.9, and Thunderbird < 102.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-09/
- https://www.mozilla.org/security/advisories/mfsa2023-10/
- https://www.mozilla.org/security/advisories/mfsa2023-11/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1808352%2C1811637%2C1815904%2C1817442%2C1818674
