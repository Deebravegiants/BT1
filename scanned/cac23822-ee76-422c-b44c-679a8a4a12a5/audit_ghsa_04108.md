# [M] Materialize-css vulnerable to Cross-site Scripting in tooltip component

## Summary
Severity: Medium
Advisory: GHSA-98f7-p5rc-jx67
CVE: CVE-2019-11002
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-04-09
Source: https://github.com/advisories/GHSA-98f7-p5rc-jx67
Type: github-advisory

## Affected
- npm: `materialize-css` — affected >=0
- npm: `@materializecss/materialize` — affected >=0 <1.1.0-alpha

## Details
All versions of `materialize-css` are vulnerable to Cross-Site Scripting. The `tooltip` component does not sufficiently sanitize user input, allowing an attacker to execute arbitrary JavaScript code if the malicious input is rendered by a user.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11002
- https://github.com/Dogfalo/materialize/issues/6286
- https://github.com/materializecss/materialize/pull/49
- https://github.com/Dogfalo/materialize
- https://github.com/advisories/GHSA-98f7-p5rc-jx67
- https://snyk.io/vuln/SNYK-JS-MATERIALIZECSS-174148
- https://www.npmjs.com/advisories/818
