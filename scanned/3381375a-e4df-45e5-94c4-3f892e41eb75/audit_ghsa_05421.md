# [H] sm-crypto Affected by Signature Forgery in SM2-DSA

## Summary
Severity: High
Advisory: GHSA-hpwg-xg7m-3p6m
CVE: CVE-2026-23965
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-hpwg-xg7m-3p6m
Type: github-advisory

## Affected
- npm: `sm-crypto` — affected >=0 <0.4.0

## Details
### Summary

A signature forgery vulnerability exists in the SM2 signature verification logic of sm-crypto. Under default configurations, an attacker can forge valid signatures for arbitrary public keys. If the message space contains sufficient redundancy, the attacker can fix the prefix of the message associated with the forged signature to satisfy specific formatting requirements.

### Credit

This vulnerability was discovered by:
- XlabAI Team of Tencent Xuanwu Lab
- Atuin Automated Vulnerability Discovery Engine

## References
- https://github.com/JuneAndGreen/sm-crypto/security/advisories/GHSA-hpwg-xg7m-3p6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-23965
- https://github.com/JuneAndGreen/sm-crypto/commit/85295a859d0766222d12ce2be3e6fce7b438b510
- https://github.com/JuneAndGreen/sm-crypto
