# [M] Open term loans can be created with zero platform service fee if borrowers create them right after a pool has been deployed.

## Summary
Severity: Medium
Contest weight: 0.0466
Dataset id: 10264
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the creation of open‑term loans with a platform service fee of zero when a borrower deploys a loan immediately after a new liquidity pool has been instantiated. The platform service fee is intended to be set at the moment a loan is deployed, but the pool contract initializes its fee variable to 0 until the fee is explicitly configured. Because the fee is read from the pool state during loan deployment, a borrower can exploit the brief window after pool creation, before the fee is updated, to launch a loan that records a zero fee. This results in the borrower avoiding the intended fee payment, causing a loss of revenue for the protocol and potentially creating an unfair advantage over other participants. The issue manifests only when a loan is created in the same transaction block or shortly thereafter, making it easy to miss during normal operation and difficult to detect from the user interface, which may simply display a fee of 0 without warning. The problem was identified during a systematic audit of the loan creation flow, where the auditor observed that the fee variable is not initialized at pool deployment and that the loan constructor copies the current fee value without validation. The bug belongs to the class of uninitialized‑state or default‑value exploitation, where default values (zero) are unintentionally accepted as valid configuration. From a user perspective, the UI may show a loan with a fee of 0, contradicting the expectation that every loan incurs a platform fee, leading to confusion or suspicion. The impact is primarily economic: the protocol forfeits fee income, and the integrity of the fee model is compromised. To remediate, the platform service fee should be assigned at the moment a loan is funded rather than at loan creation, mirroring the behavior of fixed‑term loans, or the pool should enforce a non‑zero fee invariant before any loan can be instantiated. This change ensures that the fee cannot be bypassed by timing attacks and restores the intended accounting guarantees of the system.

## Recommendation
Set the platformServiceFee when a loan is funded instead of when created, similarly to what happens on the fixed term loan.
