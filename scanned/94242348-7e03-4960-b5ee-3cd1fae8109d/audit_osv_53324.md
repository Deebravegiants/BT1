# [H] CVE-2022-38477

## Summary
Severity: High
Advisory: CVE-2022-38477
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-38477
Type: osv

## Details
Mozilla developer Nika Layzell and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 103 and Firefox ESR 102.1. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 102.2, Thunderbird < 102.2, and Firefox < 104.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-33/
- https://www.mozilla.org/security/advisories/mfsa2022-34/
- https://www.mozilla.org/security/advisories/mfsa2022-36/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1760611%2C1770219%2C1771159%2C1773363
