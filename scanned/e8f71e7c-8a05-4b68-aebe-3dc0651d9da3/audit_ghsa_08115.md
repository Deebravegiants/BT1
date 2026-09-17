# [H] cryptography Vulnerable to a Subgroup Attack Due to Missing Subgroup Validation for SECT Curves

## Summary
Severity: High
Advisory: GHSA-r6ph-v2qm-q3c2
CVE: CVE-2026-26007
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-r6ph-v2qm-q3c2
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=0 <46.0.5

## Details
## Vulnerability Summary

The `public_key_from_numbers` (or `EllipticCurvePublicNumbers.public_key()`), `EllipticCurvePublicNumbers.public_key()`, `load_der_public_key()` and `load_pem_public_key()` functions do not verify that the point belongs to the expected prime-order subgroup of the curve.

This missing validation allows an attacker to provide a public key point `P` from a small-order subgroup.  This can lead to security issues in various situations, such as the most commonly used signature verification (ECDSA) and shared key negotiation (ECDH). When the victim computes the shared secret as `S = [victim_private_key]P` via ECDH,  this leaks information about `victim_private_key mod (small_subgroup_order)`. For curves with cofactor > 1, this reveals the least significant bits of the private key.  When these weak public keys are used in ECDSA , it's easy to forge signatures on the small subgroup.

Only SECT curves are impacted by this.

## Credit

This vulnerability was discovered by:
- XlabAI Team of Tencent Xuanwu Lab
- Atuin Automated Vulnerability Discovery Engine

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-r6ph-v2qm-q3c2
- https://nvd.nist.gov/vuln/detail/CVE-2026-26007
- https://github.com/pyca/cryptography/commit/0eebb9dbb6343d9bc1d91e5a2482ed4e054a6d8c
- https://github.com/pyca/cryptography
- https://github.com/pyca/cryptography/releases/tag/46.0.5
- http://www.openwall.com/lists/oss-security/2026/02/10/4
