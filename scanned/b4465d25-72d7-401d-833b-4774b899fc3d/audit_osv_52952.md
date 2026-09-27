# [H] CVE-2022-22764

## Summary
Severity: High
Advisory: CVE-2022-22764
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22764
Type: osv

## Details
Mozilla developers Paul Adenot and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 96 and Firefox ESR 91.5. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 97, Thunderbird < 91.6, and Firefox ESR < 91.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-04/
- https://www.mozilla.org/security/advisories/mfsa2022-05/
- https://www.mozilla.org/security/advisories/mfsa2022-06/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1742682%2C1744165%2C1746545%2C1748210%2C1748279
