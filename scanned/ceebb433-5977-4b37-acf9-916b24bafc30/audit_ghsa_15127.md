# [M] Ursa CL-Signatures Revocation allows verifiers to generate unique identifiers for holders

## Summary
Severity: Medium
Advisory: GHSA-6698-mhxx-r84g
CVE: CVE-2024-22192
CWE: CWE-327
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-16
Source: https://github.com/advisories/GHSA-6698-mhxx-r84g
Type: github-advisory

## Affected
- crates.io: `ursa` — affected >=0
- crates.io: `anoncreds-clsignatures` — affected >=0 <0.1.0

## Details
### Summary

The revocation scheme that is part of the Ursa CL-Signatures implementations has a flaw that could impact the privacy guarantees defined by the AnonCreds verifiable credential model. Notably, a malicious verifier may be able to generate a unique identifier for a holder providing a verifiable presentation that includes a Non-Revocation proof.

### Details

The revocation scheme that is part of the Ursa CL-Signatures implementations has a flaw that could impact the privacy guarantees defined by the AnonCreds verifiable credential model, potentially allowing a malicious verifier to generate a unique identifier for a holder that provides a verifiable presentation that includes a Non-Revocation proof.

The flaws affects all CL-Signature versions published from the [Hyperledger Ursa] repository to the [Ursa Rust Crate], and is fixed in all versions published from the [Hyperledger AnonCreds CL-Signatures] repository to the [AnonCreds CL-Signatures Rust Crate].

The addressing the flaw requires updating AnonCreds holder software (such as mobile wallets) to a corrected CL-Signature implementation, such as the [AnonCreds CL Signatures Rust Crate]. Verifying presentations from corrected holders requires a updating the verifier software to a corrected CL-Signatures implementation. An updated verifier based on AnonCreds CL-Signatures can verify presentations from holders built on either the flawed Ursa CL-Signature implementation or a corrected CL-Signature implementation

[Hyperledger Ursa]: https://github.com/hyperledger-archives/ursa
[Ursa Rust Crate]: https://crates.io/crates/ursa
[Hyperledger AnonCreds CL-Signatures]: https://github.com/hyperledger/anoncreds-clsignatures-rs
[AnonCreds CL-Signatures Rust Crate]: https://crates.io/crates/anoncreds-clsignatures

The flaw occurs as a result of generating a verifiable presentation that includes a Non-Revocation proof from a flawed implementation.

### Impact
The impact of the flaw is that a malicious verifier may be able to determine a unique identifier for a holder presenting a Non-Revocation proof.

### Mitigation

Upgrade libraries/holder applications that generate AnonCreds verifiable presentations using the [Ursa Rust Crate] to any version of the [AnonCreds CL-Signatures Rust Crate].

## References
- https://github.com/hyperledger-archives/ursa/security/advisories/GHSA-6698-mhxx-r84g
- https://nvd.nist.gov/vuln/detail/CVE-2024-22192
- https://github.com/hyperledger/anoncreds-clsignatures-rs/commit/1e55780c890b027fa51e361e188a7743a0bf473f
- https://github.com/hyperledger-archives/ursa
