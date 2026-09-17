# [H] Command injection in smartctl

## Summary
Severity: High
Advisory: GHSA-69f2-4375-qv9h
CVE: CVE-2022-21810
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-69f2-4375-qv9h
Type: github-advisory

## Affected
- npm: `smartctl` — affected >=0

## Details
All versions of the package smartctl are vulnerable to Command Injection via the info method due to improper input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21810
- https://github.com/baslr/node-smartctl/blob/f61266084d5b3e4baae9bd85f67ec4ec6a716736/index.js#23L18
- https://github.com/baslr/node-smartctl/blob/f61266084d5b3e4baae9bd85f67ec4ec6a716736/index.js%23L18
- https://security.snyk.io/vuln/SNYK-JS-SMARTCTL-3175613
