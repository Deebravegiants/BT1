# [H] Minerva timing attack on P-256 in python-ecdsa

## Summary
Severity: High
Advisory: GHSA-wj6h-64fc-37mp
CVE: CVE-2024-23342
CWE: CWE-203, CWE-208, CWE-385
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-22
Source: https://github.com/advisories/GHSA-wj6h-64fc-37mp
Type: github-advisory

## Affected
- PyPI: `ecdsa` — affected >=0

## Details
python-ecdsa has been found to be subject to a Minerva timing attack on the P-256 curve. Using the `ecdsa.SigningKey.sign_digest()` API function and timing signatures an attacker can leak the internal nonce which may allow for private key discovery. Both ECDSA signatures, key generation, and ECDH operations are affected. ECDSA signature verification is unaffected. The python-ecdsa project considers side channel attacks out of scope for the project and there is no planned fix.

## References
- https://github.com/tlsfuzzer/python-ecdsa/security/advisories/GHSA-wj6h-64fc-37mp
- https://nvd.nist.gov/vuln/detail/CVE-2024-23342
- https://github.com/tlsfuzzer/python-ecdsa
- https://github.com/tlsfuzzer/python-ecdsa/blob/master/SECURITY.md
- https://minerva.crocs.fi.muni.cz
- https://securitypitfalls.wordpress.com/2018/08/03/constant-time-compare-in-python
