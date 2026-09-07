# [C] Remote code execution in handlebars when compiling templates

## Summary
Severity: Critical
Advisory: GHSA-f2jv-r9rf-7988
CVE: CVE-2021-23369
CWE: CWE-94
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-f2jv-r9rf-7988
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=0 <4.7.7
- Maven: `org.webjars:handlebars` — affected >=0 <4.7.7
- Maven: `org.webjars.npm:handlebars` — affected >=0 <4.7.7
- Maven: `org.webjars.bowergithub.wycats:handlebars.js` — affected >=0 <4.7.7

## Details
The package handlebars before 4.7.7 are vulnerable to Remote Code Execution (RCE) when selecting certain compiling options to compile templates coming from an untrusted source.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23369
- https://github.com/handlebars-lang/handlebars.js/commit/b6d3de7123eebba603e321f04afdbae608e8fea8
- https://github.com/handlebars-lang/handlebars.js/commit/f0589701698268578199be25285b2ebea1c1e427
- https://github.com/wycats/handlebars.js
- https://security.netapp.com/advisory/ntap-20210604-0008
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1074950
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1074951
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1074952
- https://snyk.io/vuln/SNYK-JS-HANDLEBARS-1056767
