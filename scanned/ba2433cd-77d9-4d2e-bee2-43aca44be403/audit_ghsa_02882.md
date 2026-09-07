# [C] Improper Verification of Cryptographic Signature in starkbank-ecdsa

## Summary
Severity: Critical
Advisory: GHSA-q9q6-f556-gpm7
CVE: CVE-2021-43571
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-q9q6-f556-gpm7
Type: github-advisory

## Affected
- npm: `starkbank-ecdsa` — affected >=0 <1.1.3

## Details
The verify function in the Stark Bank Node.js ECDSA library (ecdsa-node) 1.1.2 fails to check that the signature is non-zero, which allows attackers to forge signatures on arbitrary messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43571
- https://github.com/starkbank/ecdsa-node
- https://github.com/starkbank/ecdsa-node/releases/tag/v1.1.3
- https://research.nccgroup.com/2021/11/08/technical-advisory-arbitrary-signature-forgery-in-stark-bank-ecdsa-libraries
