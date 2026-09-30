# [M] CVE-2018-18499

## Summary
Severity: Medium
Advisory: CVE-2018-18499
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2018-18499
Type: osv

## Details
A same-origin policy violation allowing the theft of cross-origin URL entries when using a meta http-equiv="refresh" on a page to cause a redirection to another site using performance.getEntries(). This is a same-origin policy violation and could allow for data theft. This vulnerability affects Firefox < 62, Firefox ESR < 60.2, and Thunderbird < 60.2.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2018-20/
- https://www.mozilla.org/security/advisories/mfsa2018-21/
- https://www.mozilla.org/security/advisories/mfsa2018-25/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1468523
