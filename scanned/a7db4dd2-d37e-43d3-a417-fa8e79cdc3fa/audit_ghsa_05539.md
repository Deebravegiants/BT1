# [C] sm-crypto Affected by Private Key Recovery in SM2-PKE

## Summary
Severity: Critical
Advisory: GHSA-pgx9-497m-6c4v
CVE: CVE-2026-23966
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-pgx9-497m-6c4v
Type: github-advisory

## Affected
- npm: `sm-crypto` — affected >=0 <0.3.14

## Details
### Summary

A private key recovery vulnerability exists in the SM2 decryption logic of sm-crypto. By interacting with the SM2 decryption interface multiple times, an attacker can fully recover the private key within approximately several hundred interactions.


### Credit

This vulnerability was discovered by:
- XlabAI Team of Tencent Xuanwu Lab
- Atuin Automated Vulnerability Discovery Engine

## References
- https://github.com/JuneAndGreen/sm-crypto/security/advisories/GHSA-pgx9-497m-6c4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-23966
- https://github.com/JuneAndGreen/sm-crypto/commit/b1c824e58fdf1eaa73692c124a095819a8c45707
- https://github.com/JuneAndGreen/sm-crypto
