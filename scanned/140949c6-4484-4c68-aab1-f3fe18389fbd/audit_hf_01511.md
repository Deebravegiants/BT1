# [M] M-5 Collection shares should be limited

## Summary
Severity: Medium
Contest weight: 0.0264
Dataset id: 8007
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract implements a reward distribution mechanism that uses two share variables, each expressed with a fixed‑point scaling factor of 1e7. The code does not enforce an upper bound on these share values, allowing them to be set higher than the intended maximum of 1e7. Because later calculations assume the shares are at most 1e7, an oversized share causes arithmetic that exceeds the scaling range, triggering a require statement or causing a division by zero that makes the claim function revert every time it is called. An attacker or a careless administrator can supply a share value greater than 1e7, either deliberately or by mistake, and any user attempting to claim their reward will see the transaction fail with no funds transferred. The impact is that legitimate users are unable to receive their entitled tokens, effectively locking the reward pool and creating a denial‑of‑service condition for the reward‑claiming feature. The bug manifests only when the share parameters exceed the hidden limit, which may not be obvious during normal operation because the contract does not emit a clear error message about the share size. It was discovered during a manual audit that inspected the claim logic and noticed the absence of a bounds check on the share variables. The issue is hard to notice in testing if only valid share values are used, and the revert may be attributed to unrelated reasons by a casual observer. Conceptually, the problem belongs to the class of input‑validation bugs where critical numeric parameters are not constrained, leading to overflow or invalid arithmetic downstream. To remediate, the contract should validate that each share variable is less than or equal to the scaling factor (1e7) before they are stored or used in calculations, and should revert with a descriptive error if the check fails. From a user’s perspective the UI will show a transaction that “fails” or “reverts” when they try to claim, and the expected reward amount will never be credited, creating a mismatch between the expectation of receiving a payout and the reality of receiving nothing. This violation of the accounting assumption that total shares sum to the scaling factor breaks the protocol’s financial logic and can erode trust in the system.

## Recommendation
We recommend adding the following check: tournamentTokenShare1e7 <= 1e7 && otherTokenShare1e7 <= 1e7.
