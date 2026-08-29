# [C] zkVM Underconstrained Vulnerability

## Summary
Severity: Critical
Chain: ZK
Component: risc0/risc0
CVE: CVE-2025-52484
Published: 2025-06-18
Source: https://github.com/risc0/risc0/security/advisories/GHSA-g3qg-6746-3mg9
Type: github-advisory

## Details
Due to a missing constraint in the rv32im circuit, any 3-register RISC-V instruction (including remu and divu) in risc0-zkvm 2.0.0, 2.0.1, and 2.0.2 are vulnerable to an attack by a malicious prover. The main idea for the attack is to confuse the RISC-V virtual machine into treating the value of the rs1 register as the same as the rs2 register due to a lack of constraints in the rv32im circuit.

This vulnerability was reported by Christoph Hochrainer via our Hackenproof bug bounty. We have evaluated the severity of the vulnerability as “Critical,” and paid a bounty. 

The fix for the circuit was implemented in [zirgen/pull/238](https://github.com/risc0/zirgen/pull/238), and the update to risc0 was implemented in [risc0/pull/3181](https://github.com/risc0/risc0/pull/3181). Impacted on-chain verifiers have already been disabled via the estop mechanism outlined in the [Verifier Management Design](https://github.com/risc0/risc0-ethereum/blob/release-2.0/contracts/version-management-design.md#base-verifier-implementations). 

## Mitigation
We recommend all impacted users upgrade as soon as possible.

Rust applications using the risc0-zkvm crate at versions 2.0.0, 2.0.1, and 2.0.2 should upgrade to version 2.1.0.

Smart contract applications using the official [RISC Zero Verifier Router](https://dev.risczero.com/api/blockchain-integration/contracts/verifier#verifier-router) do not need to take any action: zkVM version 2.1 is active on all official routers, and version 2.0 has been disabled.

Smart contract applications not using the verifier router should update their contracts to send verification calls to the 2.1 version of the verifier.
