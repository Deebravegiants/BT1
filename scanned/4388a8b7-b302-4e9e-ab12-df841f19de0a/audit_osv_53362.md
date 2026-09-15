# [H] CVE-2022-40962

## Summary
Severity: High
Advisory: CVE-2022-40962
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-40962
Type: osv

## Details
Mozilla developers Nika Layzell, Timothy Nikkel, Sebastian Hengst, Andreas Pehrson, and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 104 and Firefox ESR 102.2. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 102.3, Thunderbird < 102.3, and Firefox < 105.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-41/
- https://www.mozilla.org/security/advisories/mfsa2022-42/
- https://www.mozilla.org/security/advisories/mfsa2022-40/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1776655%2C1777574%2C1784835%2C1785109%2C1786502%2C1789440
