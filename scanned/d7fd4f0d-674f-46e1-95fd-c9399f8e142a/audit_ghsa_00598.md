# [M] Pandao editor.md vulnerable to DOM XSS

## Summary
Severity: Medium
Advisory: GHSA-x3g3-334f-q6h4
CVE: CVE-2018-19056
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-x3g3-334f-q6h4
Type: github-advisory

## Affected
- npm: `editor.md` — affected 1.5.0

## Details
pandao Editor.md 1.5.0 has DOM XSS via input starting with a `<<` substring, which is mishandled during construction of an `A` element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19056
- https://github.com/pandao/editor.md/issues/634
- https://github.com/advisories/GHSA-x3g3-334f-q6h4
- https://github.com/pandao/editor.md
