# [C] CVE-2022-29917

## Summary
Severity: Critical
Advisory: CVE-2022-29917
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-29917
Type: osv

## Details
Mozilla developers Andrew McCreight, Gabriele Svelto, Tom Ritter and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 99 and Firefox ESR 91.8. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Thunderbird < 91.9, Firefox ESR < 91.9, and Firefox < 100.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-18/
- https://www.mozilla.org/security/advisories/mfsa2022-16/
- https://www.mozilla.org/security/advisories/mfsa2022-17/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1684739%2C1706441%2C1753298%2C1762614%2C1762620%2C1764778
