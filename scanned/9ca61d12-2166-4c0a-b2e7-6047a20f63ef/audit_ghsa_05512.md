# [H] sm-crypto Affected by Signature Malleability in SM2-DSA

## Summary
Severity: High
Advisory: GHSA-qv7w-v773-3xqm
CVE: CVE-2026-23967
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-qv7w-v773-3xqm
Type: github-advisory

## Affected
- npm: `sm-crypto` — affected >=0 <0.3.14

## Details
### Summary

A signature malleability vulnerability exists in the SM2 signature verification logic of the sm-crypto library. An attacker can derive a new valid signature for a previously signed message from an existing signature.

### Credit

This vulnerability was discovered by:
- XlabAI Team of Tencent Xuanwu Lab
- Atuin Automated Vulnerability Discovery Engine

## References
- https://github.com/JuneAndGreen/sm-crypto/security/advisories/GHSA-qv7w-v773-3xqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-23967
- https://github.com/JuneAndGreen/sm-crypto
