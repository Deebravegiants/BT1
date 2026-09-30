# [H] OS Command Injection in enpeem

## Summary
Severity: High
Advisory: GHSA-hmw2-mvvh-jf5j
CVE: CVE-2019-10801
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-hmw2-mvvh-jf5j
Type: github-advisory

## Affected
- npm: `enpeem` — affected >=0

## Details
enpeem through 2.2.0 allows execution of arbitrary commands. The &quot;options.dir&quot; argument is provided to the &quot;exec&quot; function without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10801
- https://github.com/balderdashy/enpeem/blob/master/index.js#L114
- https://snyk.io/vuln/SNYK-JS-ENPEEM-559007
