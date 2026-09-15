# [M] CL-Signatures Revocation Scheme in Ursa has flaws that allow a holder to demonstrate non-revocation of a revoked credential

## Summary
Severity: Medium
Advisory: GHSA-r78f-4q2q-hvv4
CVE: CVE-2024-21670
CWE: CWE-327
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:P/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-16
Source: https://github.com/advisories/GHSA-r78f-4q2q-hvv4
Type: github-advisory

## Affected
- crates.io: `ursa` — affected >=0
- crates.io: `anoncreds-clsignatures` — affected >=0

## Details
### Summary

The revocation schema that is part of the Ursa CL-Signatures implementations has a flaw that could impact the privacy guarantees defined by the AnonCreds verifiable credential model, allowing a malicious holder of a revoked credential to generate a valid Non-Revocation Proof for that credential as part of an AnonCreds presentation.

### Details

The revocation schema that is part of the Ursa CL-Signatures implementation has a flaw that could impact the privacy guarantees defined by the AnonCreds verifiable credential model, allowing a malicious holder of a revoked credential to generate a valid Non-Revocation Proof for that credential as part of an AnonCreds presentation.

The flaw exists in all CL-Signature versions published from the [Hyperledger Ursa] repository to the [Ursa Rust Crate], and are fixed in all versions published from the [Hyperledger AnonCreds CL-Signatures] repository to the [AnonCreds CL-Signatures Rust Crate].

To exploit the flaw, a holder must update their wallet (agent) software, replacing the Hyperledger Ursa or AnonCreds CL-Signatures library that generates the proof of non-revocation. This may involve, for example, altering an iOS or Android application published in the respective app stores. A mitigation for this flaw is to use the application attestation capabilities (such as the Android "[SafetyNet Attestation API]") offered by the app store vendors to (for example) "help determine whether your servers are interacting with your genuine app running on a genuine Android device."

The problem is created in the generation of a revocation registry, prior to issuing any credentials. As such, to eliminate the impact of the flaw, the issued credentials must be re-issued based on a correct revocation registry, generated from a correct implementation, such as [Hyperledger AnonCreds CL-Signatures].

[Hyperledger Ursa]: https://github.com/hyperledger-archives/ursa
[Ursa Rust Crate]: https://crates.io/crates/ursa
[Hyperledger AnonCreds CL-Signatures]: https://github.com/hyperledger/anoncreds-clsignatures-rs
[AnonCreds CL-Signatures Rust Crate]: https://crates.io/crates/anoncreds-clsignatures
[SafetyNet Attestation API]: https://developer.android.com/privacy-and-security/safetynet/attestation
### Impact
The potential impact is as follows:

- A verifier may verify a credential from a holder as being "not revoked" when in fact, the holder's credential has been revoked.

### Mitigation

Upgrade libraries/applications using the [Ursa Rust Crate] to any version of the [AnonCreds CL-Signatures Rust Crate]. If your application has issued revocable credentials, once the Issuer library has been upgraded, new revocation registries must be created, and credentials issued from revocation registries created with the the flawed software must be revoked and reissued.

A verifier can detect if a holder presents a flawed revocable credential.

## References
- https://github.com/hyperledger-archives/ursa/security/advisories/GHSA-r78f-4q2q-hvv4
- https://nvd.nist.gov/vuln/detail/CVE-2024-21670
- https://github.com/hyperledger-archives/ursa
