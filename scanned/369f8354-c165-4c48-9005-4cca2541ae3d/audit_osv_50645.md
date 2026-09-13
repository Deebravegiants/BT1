# [H] CVE-2020-26968

## Summary
Severity: High
Advisory: CVE-2020-26968
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26968
Type: osv

## Details
Mozilla developers reported memory safety bugs present in Firefox 82 and Firefox ESR 78.4. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 83, Firefox ESR < 78.5, and Thunderbird < 78.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-50/
- https://www.mozilla.org/security/advisories/mfsa2020-51/
- https://www.mozilla.org/security/advisories/mfsa2020-52/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1551615%2C1607762%2C1656697%2C1657739%2C1660236%2C1667912%2C1671479%2C1671923
