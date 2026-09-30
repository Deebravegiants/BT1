# [M] M-12 Possible division by zero

## Summary
Severity: Medium
Contest weight: 0.0303
Dataset id: 7989
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a calculation that divides a reward amount by a variable representing total basis points (BPS). The code does not verify that the BPS value is non‑zero before performing the division. If the total BPS for a tournament or for other categories is zero, the division operation triggers a Solidity runtime exception (division‑by‑zero) which reverts the whole transaction. This can happen when no participants have contributed to a tournament, or when the contract state is reset incorrectly, leaving the total BPS at its default value of zero. An attacker or any user invoking the claim function under those conditions will cause the function to revert, preventing the distribution of any pending rewards. The immediate impact is a denial‑of‑service for legitimate claimers: users see no refund, balances appear unchanged, and the UI may show a generic “transaction failed” message. Because the failure occurs deep inside a mathematical expression, it may be difficult to notice during normal testing unless the specific zero‑BPS scenario is exercised. The issue was discovered during a manual audit that inspected the claim logic and identified missing guard clauses. The bug belongs to the class of arithmetic‑validation errors, where insufficient input validation leads to runtime exceptions. To remediate, the contract should explicitly check that each total‑BPS variable is greater than zero before performing the division; if it is zero, the claim amount should be set to zero or the function should return early. Adding these checks restores the intended business logic that a claim is proportional to the total BPS and prevents funds from becoming inaccessible due to a revert.

## Recommendation
We recommend adding a check that if tournamentTotalBPS == 0, then tournamentClaim = 0 and the same check for otherTotalBPS == 0.
