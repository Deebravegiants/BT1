# [H] CVE-2022-2505

## Summary
Severity: High
Advisory: CVE-2022-2505
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-2505
Type: osv

## Details
Mozilla developers and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 102. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 102.1, Firefox < 103, and Thunderbird < 102.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-28/
- https://www.mozilla.org/security/advisories/mfsa2022-30/
- https://www.mozilla.org/security/advisories/mfsa2022-32/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1769739%2C1772824
