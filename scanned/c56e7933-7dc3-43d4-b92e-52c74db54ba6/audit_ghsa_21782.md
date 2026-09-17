# [C] Prototype Pollution in handlebars

## Summary
Severity: Critical
Advisory: GHSA-765h-qjxv-5f44
CVE: CVE-2021-23383
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-765h-qjxv-5f44
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=0 <4.7.7

## Details
The package handlebars before 4.7.7 are vulnerable to Prototype Pollution when selecting certain compiling options to compile templates coming from an untrusted source.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23383
- https://github.com/handlebars-lang/handlebars.js/commit/f0589701698268578199be25285b2ebea1c1e427
- https://github.com/handlebars-lang/handlebars.js
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/handlebars-source/CVE-2021-23383.yml
- https://security.netapp.com/advisory/ntap-20210618-0007
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1279031
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1279032
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1279030
- https://snyk.io/vuln/SNYK-JS-HANDLEBARS-1279029
- https://www.npmjs.com/package/handlebars
