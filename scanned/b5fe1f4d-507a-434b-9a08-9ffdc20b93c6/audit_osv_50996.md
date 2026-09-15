# [C] CVE-2020-6825

## Summary
Severity: Critical
Advisory: CVE-2020-6825
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-24
Source: https://osv.dev/vulnerability/CVE-2020-6825
Type: osv

## Details
Mozilla developers and community members Tyson Smith and Christian Holler reported memory safety bugs present in Firefox 74 and Firefox ESR 68.6. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Thunderbird < 68.7.0, Firefox ESR < 68.7, and Firefox < 75.

## References
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-12/
- https://www.mozilla.org/security/advisories/mfsa2020-13/
- https://www.mozilla.org/security/advisories/mfsa2020-14/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1572541%2C1620193%2C1620203
