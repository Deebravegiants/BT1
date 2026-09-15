# [H] Regular Expression Denial of Service in Handlebars

## Summary
Severity: High
Advisory: GHSA-62gr-4qp9-h98f
CVE: CVE-2019-20922
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-62gr-4qp9-h98f
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.0.0 <4.4.5

## Details
Handlebars before 4.4.5 allows Regular Expression Denial of Service (ReDoS) because of eager matching. The parser may be forced into an endless loop while processing crafted templates. This may allow attackers to exhaust system resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20922
- https://github.com/handlebars-lang/handlebars.js/commit/8d5530ee2c3ea9f0aee3fde310b9f36887d00b8b
- https://snyk.io/vuln/SNYK-JS-HANDLEBARS-480388
- https://www.npmjs.com/advisories/1300
- https://www.npmjs.com/package/handlebars
