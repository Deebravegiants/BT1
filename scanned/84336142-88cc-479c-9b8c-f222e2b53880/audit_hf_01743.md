# [M] M-1 Extra function

## Summary
Severity: Medium
Contest weight: 0.0404
Dataset id: 9529
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains two functions that perform almost identical operations, but only one of them updates the accounting variable that tracks the total MEV transaction fee collected (TOTALMEVTXFEECOLLECTED_POSITION). The other function executes the same core logic without modifying this state variable, making it effectively redundant. This discrepancy originates from a copy‑paste or design oversight where the second function was left without the necessary state mutation. An attacker or any caller who can invoke the redundant function can trigger the intended protocol actions while bypassing the fee accounting update, causing the protocol’s internal accounting to diverge from the actual economic activity. The impact is that the protocol may report lower fee totals than were truly earned, leading to inaccurate revenue distribution, potential underpayment of stakeholders, and a breach of the accounting invariants that users rely on. The issue manifests whenever the redundant function is called, which could happen unintentionally through a user interface that exposes both functions or deliberately by a malicious actor seeking to hide fee collection. All participants that depend on correct fee accounting – such as token holders, delegators, and the protocol’s governance mechanisms – are affected because the reported fee totals no longer reflect reality. The problem was identified during a systematic security audit performed by MixBytes, which flagged the duplicated code paths and the missing state update as a medium‑severity concern. Because the two functions look very similar, the omission is easy to overlook during code reviews and testing, especially if the test suite only checks functional outcomes without verifying internal state changes. To remediate the issue, the redundant function should be removed entirely, or its implementation should be aligned with the primary function to ensure that TOTALMEVTXFEECOLLECTED_POSITION is updated consistently in every execution path. This correction restores the integrity of the fee accounting logic, prevents potential revenue leakage, and eliminates an unnecessary attack surface.

## Recommendation
Need to remove the redundant feature.
