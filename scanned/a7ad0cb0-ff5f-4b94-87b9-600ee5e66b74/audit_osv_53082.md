# [H] CVE-2022-28289

## Summary
Severity: High
Advisory: CVE-2022-28289
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-28289
Type: osv

## Details
Mozilla developers and community members Nika Layzell, Andrew McCreight, Gabriele Svelto, and the Mozilla Fuzzing Team reported memory safety bugs present in Thunderbird 91.7. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Thunderbird < 91.8, Firefox < 99, and Firefox ESR < 91.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-15/
- https://www.mozilla.org/security/advisories/mfsa2022-13/
- https://www.mozilla.org/security/advisories/mfsa2022-14/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1663508%2C1744525%2C1753508%2C1757476%2C1757805%2C1758549%2C1758776
