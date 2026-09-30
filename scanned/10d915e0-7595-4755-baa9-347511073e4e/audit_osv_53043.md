# [H] CVE-2022-26381

## Summary
Severity: High
Advisory: CVE-2022-26381
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-26381
Type: osv

## Details
An attacker could have caused a use-after-free by forcing a text reflow in an SVG object leading to a potentially exploitable crash. This vulnerability affects Firefox < 98, Firefox ESR < 91.7, and Thunderbird < 91.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-10/
- https://www.mozilla.org/security/advisories/mfsa2022-11/
- https://www.mozilla.org/security/advisories/mfsa2022-12/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1736243
