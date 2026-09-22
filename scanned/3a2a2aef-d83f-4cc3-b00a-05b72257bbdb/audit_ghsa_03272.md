# [H] Command injection in portkiller

## Summary
Severity: High
Advisory: GHSA-r6fw-8m27-43c9
CVE: CVE-2021-23379
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-r6fw-8m27-43c9
Type: github-advisory

## Affected
- npm: `portkiller` — affected >=0

## Details
This affects all versions of package portkiller. If (attacker-controlled) user input is given, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23379
- https://github.com/indatawetrust/portkiller
- https://github.com/indatawetrust/portkiller/blob/f1f1c5076d9c5d60e8dd3930e98d665d8191aa7a/index.js%23L10
- https://snyk.io/vuln/SNYK-JS-PORTKILLER-1078537
- https://www.npmjs.com/package/portkiller
