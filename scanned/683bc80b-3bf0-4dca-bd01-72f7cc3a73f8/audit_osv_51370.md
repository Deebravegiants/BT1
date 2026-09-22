# [H] CVE-2021-29976

## Summary
Severity: High
Advisory: CVE-2021-29976
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-29976
Type: osv

## Details
Mozilla developers reported memory safety bugs present in code shared between Firefox and Thunderbird. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Thunderbird < 78.12, Firefox ESR < 78.12, and Firefox < 90.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-28/
- https://www.mozilla.org/security/advisories/mfsa2021-29/
- https://www.mozilla.org/security/advisories/mfsa2021-30/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1700895%2C1703334%2C1706910%2C1711576%2C1714391
- https://security.gentoo.org/glsa/202202-03
- https://security.gentoo.org/glsa/202208-14
