# [H] seroval Affected by Prototype Pollution via JSON Deserialization

## Summary
Severity: High
Advisory: GHSA-hj76-42vx-jwp4
CVE: CVE-2026-23736
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-hj76-42vx-jwp4
Type: github-advisory

## Affected
- npm: `seroval` — affected >=0 <1.4.1

## Details
Due to improper input validation, a malicious object key can lead to prototype pollution during JSON deserialization.
This affects only JSON deserialization functionality.

As there is no known workaround, please upgrade to the latest version.

## References
- https://github.com/lxsmnsyc/seroval/security/advisories/GHSA-hj76-42vx-jwp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-23736
- https://github.com/lxsmnsyc/seroval/commit/ce9408ebc87312fcad345a73c172212f2a798060
- https://github.com/lxsmnsyc/seroval
