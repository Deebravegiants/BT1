# [M] Insufficient observation of cumulative sum

## Summary
Severity: Medium
Chain: ZK
Component: succinctlabs/sp1
Published: 2024-11-08
Source: https://github.com/succinctlabs/sp1/security/advisories/GHSA-8m24-3cfx-9fjw
Type: github-advisory

## Details
During proof generation, the prover must observe all values sent to the verifier to generate valid Fiat-Shamir challenges. Prior to v3.0.0 the cumulative sum of the permutation argument was not observed when sampling zeta, which is a random challenge sampled to force the constraints to be true. In v3.0.0, this is fixed by observing the cumulative sum into the challenger, which can is done by observing the commit to the entire permutation trace.

While this vulnerability is theoretically present in v2.0.0 and below, exploiting it is quite a difficult task as the cumulative sum one can get from manipulation is essentially random. It requires practically infeasible amount of computation and deep knowledge of cryptographic attacks to carry out.

This issue was discovered during the audit of SP1 V3.0.0 and was officially fixed on October 17th. Out of abundance of caution, we will be deprecating all versions of SP1 before 3.0.0.
