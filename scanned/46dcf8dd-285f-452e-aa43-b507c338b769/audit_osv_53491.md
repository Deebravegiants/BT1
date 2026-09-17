# [H] CVE-2022-45421

## Summary
Severity: High
Advisory: CVE-2022-45421
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45421
Type: osv

## Details
Mozilla developers Andrew McCreight and Gabriele Svelto reported memory safety bugs present in Thunderbird 102.4. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1767920%2C1789808%2C1794061
