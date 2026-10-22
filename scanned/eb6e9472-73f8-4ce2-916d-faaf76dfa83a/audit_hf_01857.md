# [M] M-12 duration is not limited

## Summary
Severity: Medium
Contest weight: 0.0371
Dataset id: 10358
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the handling of the proposal duration field in the DAO governance contract. The contract creates proposals without persisting the duration value and without imposing any upper bound on the value that can be supplied. Because the duration is not stored, later logic that assumes a valid, bounded duration may read an uninitialized or default value, or may accept an arbitrarily large number supplied at creation time. This omission originates from a missing assignment in the proposal‑initialisation routine and the absence of validation checks on the input parameter. An attacker can exploit the flaw by submitting a proposal with an excessively large duration, effectively making the proposal never reach its expiry condition. As a result, the proposal remains permanently active, preventing any veto, execution, or fund release that depends on the expiry event. The impact is a potential governance deadlock: token holders and DAO participants expect proposals to resolve after a reasonable time, but the contract may keep them open indefinitely, causing funds to stay locked, rewards to be withheld, and the overall protocol to lose its ability to progress. The issue manifests whenever a new proposal is created, and it can be triggered by any user who can call the proposal‑creation function, because there is no role‑based restriction on the duration argument. The problem was discovered during a systematic security audit performed by MixBytes, which identified that the duration variable is not saved (as noted in a high‑severity comment) and that the code lacks any limit enforcement. The bug is subtle because the user interface may still display a deadline based on the input value, giving the impression that the deadline is enforced, while the contract’s internal state does not reflect this constraint. To remediate the issue, the duration should be stored as part of the proposal data structure and a maximum allowable duration should be defined and enforced at creation time. Additionally, the contract should reject proposals with zero or negative durations and provide a mechanism to update or correct the duration if needed. By ensuring the duration is persisted and bounded, the governance logic will correctly transition proposals to their terminal state, restoring expected fund flows and preventing indefinite locking of assets.

## Recommendation
We recommend limiting duration because it will be saved for proposals without the ability to update it.
