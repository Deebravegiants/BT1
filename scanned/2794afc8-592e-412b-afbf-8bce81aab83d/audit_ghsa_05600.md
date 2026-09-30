# [C] dcap-qvl has Missing Verification for QE Identity

## Summary
Severity: Critical
Advisory: GHSA-796p-j2gh-9m2q
CVE: CVE-2026-22696
CWE: CWE-295, CWE-347
Ecosystem: PyPI, crates.io, npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-796p-j2gh-9m2q
Type: github-advisory

## Affected
- crates.io: `dcap-qvl` — affected >=0 <0.3.9
- npm: `@phala/dcap-qvl` — affected >=0 <0.3.9
- npm: `@phala/dcap-qvl-web` — affected >=0
- npm: `@phala/dcap-qvl-node` — affected >=0
- PyPI: `dcap-qvl` — affected >=0 <0.3.9

## Details
## Impact
This vulnerability involves a critical gap in the cryptographic verification process within the dcap-qvl.

The library fetches QE Identity collateral (including qe_identity, qe_identity_signature, and qe_identity_issuer_chain) from the PCCS. However, it skips to verify the QE Identity signature against its certificate chain and does not enforce policy constraints on the QE Report.

## Consequences
An attacker can forge the QE Identity data to whitelist a malicious or non-Intel Quoting Enclave. This allows the attacker to forge the QE and sign untrusted quotes that the verifier will accept as valid. Effectively, this bypasses the entire remote attestation security model, as the verifier can no longer trust the entity responsible for signing the quotes.

## Who is impacted
All deployments utilizing the dcap-qvl library for SGX or TDX quote verification are affected.

## Patches
The vulnerability has been patched in dcap-qvl version 0.3.9. The fix implements the missing cryptographic verification for the QE Identity signature and enforces the required checks for MRSIGNER, ISVPRODID, and ISVSVN against the QE Report.

Users of the `@phala/dcap-qvl-node` and `@phala/dcap-qvl-web` packages should switch to the pure JavaScript implementation, `@phala/dcap-qvl`.

## Workarounds
There are no known workarounds for this vulnerability. Users must upgrade to the patched version to ensure that QE Identity collateral is properly verified.

## Credit
This bug was reported by Rahul Saxena <saxenism@bluethroatlabs.com>.

## References
- https://github.com/Phala-Network/dcap-qvl/security/advisories/GHSA-796p-j2gh-9m2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-22696
- https://github.com/Phala-Network/dcap-qvl
