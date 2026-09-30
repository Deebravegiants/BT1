# [M] M-9 Escrows can be reused

## Summary
Severity: Medium
Contest weight: 0.0287
Dataset id: 10405
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the ability to reuse escrow contracts that were intended to be single‑use. The escrow logic includes a condition that determines whether the locked funds may be released to the beneficiary. Because the contract does not enforce a one‑time execution flag or reset the condition safely, the same escrow instance can be invoked a second time. The root cause is the absence of state protection that guarantees the condition is evaluated correctly only once; after the first execution the internal state may remain unchanged or become inconsistent, allowing a subsequent call to bypass the original checks. An attacker or any user who can trigger a second execution can therefore cause the escrow to release funds under an unintended circumstance, such as sending the assets to an address that was not part of the original agreement or keeping the funds locked indefinitely. The impact ranges from partial loss of funds to complete theft, depending on how the condition is mis‑evaluated. This issue manifests when the escrow contract is called more than once, which can happen in normal operation if the contract is reused, or through a malicious re‑entry pattern that deliberately invokes the release function again. All participants that rely on the escrow – the depositor, the intended beneficiary, and the broader protocol that assumes escrow finality – are affected because the financial guarantees of the escrow are broken. The flaw was discovered during a systematic security audit that examined state transitions and identified that the contract does not set a “used” flag or otherwise prevent a second execution. Because the contract still appears to function correctly on the first call, the problem can be hard to notice; only after a second call does the incorrect behavior surface, often showing up as a missing refund or an unexpected zero balance for the depositor. To remediate, the escrow should be redesigned as a single‑use primitive: after a successful release, the contract must mark itself as completed and reject any further calls, or it should be destroyed. Alternatively, the condition logic must be made idempotent and include explicit checks that the escrow has not been previously settled. This class of bug belongs to improper state management in financial primitives, where reuse of a mutable escrow leads to accounting errors, fund disappearance, and violation of the protocol’s trust model.

## Recommendation
We recommend restricting the usage of the escrows more than one time.
