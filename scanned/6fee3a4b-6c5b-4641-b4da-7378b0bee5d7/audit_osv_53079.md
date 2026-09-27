# [M] CVE-2022-28282

## Summary
Severity: Medium
Advisory: CVE-2022-28282
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-28282
Type: osv

## Details
By using a link with <code>rel="localization"</code> a use-after-free could have been triggered by destroying an object during JavaScript execution and then referencing the object through a freed pointer, leading to a potential exploitable crash. This vulnerability affects Thunderbird < 91.8, Firefox < 99, and Firefox ESR < 91.8.

## References
- https://bugzilla.mozilla.org/show_bug.cgi?id=1751609
- https://www.mozilla.org/security/advisories/mfsa2022-13/
- https://www.mozilla.org/security/advisories/mfsa2022-14/
- https://www.mozilla.org/security/advisories/mfsa2022-15/
