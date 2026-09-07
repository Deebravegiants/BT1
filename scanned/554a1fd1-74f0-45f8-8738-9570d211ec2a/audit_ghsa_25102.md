# [M] materialize-css vulnerable to cross-site Scripting (XSS) due to improper escape of user input

## Summary
Severity: Medium
Advisory: GHSA-7jvx-f994-rfw2
CVE: CVE-2022-25349
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-7jvx-f994-rfw2
Type: github-advisory

## Affected
- npm: `materialize-css` — affected >=0

## Details
All versions of package materialize-css are vulnerable to Cross-site Scripting (XSS) due to improper escape of user input (such as &lt;not-a-tag /&gt;) that is being parsed as HTML/JavaScript, and inserted into the Document Object Model (DOM). This vulnerability can be exploited when the user-input is provided to the autocomplete component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25349
- https://github.com/Dogfalo/materialize
- https://github.com/Dogfalo/materialize/blob/v1-dev/js/autocomplete.js%23L285%20
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2766498
- https://snyk.io/vuln/SNYK-JS-MATERIALIZECSS-2324800
