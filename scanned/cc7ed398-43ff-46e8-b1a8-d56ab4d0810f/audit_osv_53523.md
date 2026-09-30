# [H] CVE-2022-46878

## Summary
Severity: High
Advisory: CVE-2022-46878
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-46878
Type: osv

## Details
Mozilla developers Randell Jesup, Valentin Gosu, Olli Pettay, and the Mozilla Fuzzing Team reported memory safety bugs present in Thunderbird 102.5. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 108, Firefox ESR < 102.6, and Thunderbird < 102.6.

## References
- https://security.gentoo.org/glsa/202305-06
- https://security.gentoo.org/glsa/202305-13
- https://www.mozilla.org/security/advisories/mfsa2022-51/
- https://www.mozilla.org/security/advisories/mfsa2022-52/
- https://www.mozilla.org/security/advisories/mfsa2022-53/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1782219%2C1797370%2C1797685%2C1801102%2C1801315%2C1802395
