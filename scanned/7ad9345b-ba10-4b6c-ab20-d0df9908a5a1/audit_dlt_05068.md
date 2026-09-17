# [H] Insufficient zkVM validation of multi-step instruction modes

## Summary
Severity: High
Chain: ZK
Component: risc0/risc0
Published: 2024-09-25
Source: https://github.com/risc0/risc0/security/advisories/GHSA-5c79-r6x7-3jx9
Type: github-advisory

## Details
Certain RISC-V instructions require multiple zkVM cycles for execution. During the first cycle of a multi-cycle instruction the zkVM sets a ```major mode``` which tells the zkVM how to continue the instruction during the subsequent cycle.

Prior to ```v1.1.1```, the zkVM did not impose a subsequent constraint to ensure that the mode of operation had definitively been set by the previous instruction.  As of 1.1.1 these constraints have been added to ensure that the mode was selected by the previous cycle.

While it is unclear if this condition is exploitable, critical applications should consider this to be a security flaw and assume that an abuse case exists in which an attacker can generate invalid proofs that successfully verify.

Out of an abundance of caution RISC Zero official verifier contracts will deprecate verification of ```<1.1.1``` receipts as of October 31, 2024.
