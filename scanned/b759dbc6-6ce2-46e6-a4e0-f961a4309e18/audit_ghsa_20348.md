# [H] OS Command Injection in s3-uploader

## Summary
Severity: High
Advisory: GHSA-gwp3-f7mr-qpfv
CVE: CVE-2021-34084
CWE: CWE-78
Ecosystem: npm
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-gwp3-f7mr-qpfv
Type: github-advisory

## Affected
- npm: `s3-uploader` — affected >=0

## Details
OS command injection vulnerability in Turistforeningen node-s3-uploader through 2.0.3 for Node.js allows attackers to execute arbitrary commands via the metadata() function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34084
- https://advisory.checkmarx.net/advisory/CX-2021-4776
- https://github.com/Turistforeningen/node-s3-uploader
