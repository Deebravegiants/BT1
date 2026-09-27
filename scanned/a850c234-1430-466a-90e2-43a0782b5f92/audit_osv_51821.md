# [C] CVE-2021-4129

## Summary
Severity: Critical
Advisory: CVE-2021-4129
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2021-4129
Type: osv

## Details
Mozilla developers and community members Julian Hector, Randell Jesup, Gabriele Svelto, Tyson Smith, Christian Holler, and Masayuki Nakano reported memory safety bugs present in Firefox 94. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 95, Firefox ESR < 91.4.0, and Thunderbird < 91.4.0.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-52/
- https://www.mozilla.org/security/advisories/mfsa2021-53/
- https://www.mozilla.org/security/advisories/mfsa2021-54/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1393362%2C1736046%2C1736751%2C1737009%2C1739372%2C1739421
