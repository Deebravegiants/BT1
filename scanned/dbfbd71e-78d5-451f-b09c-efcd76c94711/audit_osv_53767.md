# [H] CVE-2023-23605

## Summary
Severity: High
Advisory: CVE-2023-23605
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-23605
Type: osv

## Details
Mozilla developers and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 108 and Firefox ESR 102.6. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 109, Firefox ESR < 102.7, and Thunderbird < 102.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-01/
- https://www.mozilla.org/security/advisories/mfsa2023-02/
- https://www.mozilla.org/security/advisories/mfsa2023-03/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1764921%2C1802690%2C1806974
