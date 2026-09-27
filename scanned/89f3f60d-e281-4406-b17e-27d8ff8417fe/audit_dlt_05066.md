# [M] Underconstrained Vulnerability: Division

## Summary
Severity: Medium
Chain: ZK
Component: risc0/risc0
CVE: CVE-2025-54873
Published: 2025-08-04
Source: https://github.com/risc0/risc0/security/advisories/GHSA-f6rc-24x4-ppxp
Type: github-advisory

## Details
Two issues were found: For some inputs to signed integer division, the circuit allowed two outputs, only one of which was valid.  Additionally, the result of division by zero was underconstrained.

This vulnerability was identified using the Picus tool from Veridise. 

Impacted on-chain verifiers have already been disabled via the estop mechanism outlined in the [Verifier Management Design](https://github.com/risc0/risc0-ethereum/blob/release-2.0/contracts/version-management-design.md#base-verifier-implementations). 

## Mitigation

We recommend all impacted users upgrade as soon as possible.

Rust applications using the `risc0-zkvm` crate at versions < 2.2 should upgrade to version 2.2.0 or later. 

Smart contract applications using the official [RISC Zero Verifier Router](https://dev.risczero.com/api/blockchain-integration/contracts/verifier#verifier-router) do not need to take any action: zkVM version 2.2 is active on all official routers, and version 2.1 has been disabled.

Smart contract applications not using the verifier router should update their contracts to send verification calls to the 2.2 version of the verifier.

## References

* https://github.com/risc0/zirgen/pull/249
* https://github.com/risc0/risc0/pull/3235
