# [M] Cross-site Scripting in aurelia-framework

## Summary
Severity: Medium
Advisory: GHSA-m6j2-v3gq-45r5
CVE: CVE-2019-10062
CWE: CWE-79
Ecosystem: npm
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-m6j2-v3gq-45r5
Type: github-advisory

## Affected
- npm: `aurelia-framework` — affected >=0 <1.4.1

## Details
The HTMLSanitizer class in html-sanitizer.ts in all released versions of the Aurelia framework 1.x repository is vulnerable to XSS. The sanitizer only attempts to filter SCRIPT elements, which makes it feasible for remote attackers to conduct XSS attacks via (for example) JavaScript code in an attribute of various other elements. An attacker might also exploit a bug in how the SCRIPT string is processed by splitting and nesting them for example.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10062
- https://github.com/aurelia/framework/issues/992
- https://discourse.aurelia.io/t/xss-vulnerability-in-htmlsanitizer-might-be-insufficiently-handled/4219
- https://github.com/aurelia/framework
- https://github.com/aurelia/templating-resources/blob/0cef07a8cac8e99146d8e1c4b734491bb3dc4724/src/html-sanitizer.js
- https://www.gosecure.net/blog/2021/05/12/aurelia-framework-insecure-default-allows-xss
