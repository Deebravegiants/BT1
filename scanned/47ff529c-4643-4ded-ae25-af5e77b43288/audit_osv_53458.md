# [H] CVE-2022-42932

## Summary
Severity: High
Advisory: CVE-2022-42932
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-42932
Type: osv

## Details
Mozilla developers Ashley Hale and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 105 and Firefox ESR 102.3. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 106, Firefox ESR < 102.4, and Thunderbird < 102.4.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-44/
- https://www.mozilla.org/security/advisories/mfsa2022-45/
- https://www.mozilla.org/security/advisories/mfsa2022-46/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1789729%2C1791363%2C1792041
