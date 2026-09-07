# [M] vue-template-compiler vulnerable to client-side Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-g3ch-rx76-35fx
CVE: CVE-2024-6783
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-23
Source: https://github.com/advisories/GHSA-g3ch-rx76-35fx
Type: github-advisory

## Affected
- npm: `vue-template-compiler` — affected >=2.0.0

## Details
A vulnerability has been discovered in vue-template-compiler, that allows an attacker to perform XSS via prototype pollution. The attacker could change the prototype chain of some properties such as `Object.prototype.staticClass` or `Object.prototype.staticStyle` to execute arbitrary JavaScript code. Vue 2 has reached End-of-Life. This vulnerability has been patched in Vue 3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6783
- https://github.com/vuejs/vue
- https://www.herodevs.com/vulnerability-directory/cve-2024-6783
