# [M] Zowe CLI allows storage of previously entered secure credentials in a plaintext file

## Summary
Severity: Medium
Advisory: GHSA-ghgq-x6wc-6jr5
CVE: CVE-2024-6833
CWE: CWE-256
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-ghgq-x6wc-6jr5
Type: github-advisory

## Affected
- npm: `@zowe/cli` — affected >=7.18.0 <7.23.5

## Details
A vulnerability in Zowe CLI allows local, privileged actors to store previously entered secure credentials in a plaintext file as part of an auto-init operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6833
- https://github.com/zowe/zowe-cli/commit/6778da5e03c65dfcd3e6e4b4097b94d9fbd5d01b
- https://github.com/zowe/zowe-cli
