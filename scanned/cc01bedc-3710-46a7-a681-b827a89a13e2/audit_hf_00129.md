# [M] pendingWithdrawals just increments

## Summary
Severity: Medium
Contest weight: 0.0390
Dataset id: 384
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability arises from an accounting flaw in the contract’s withdrawal logic. When a user invokes the withdraw function, the contract records the amount that the user is entitled to in a variable commonly referred to as pendingWithdrawals. However, the implementation only increments this pending amount and never decrements it after the funds have been transferred out. Consequently, the contract’s internal ledger continues to believe that the user still has a claim on the same funds, even though the tokens have already been sent. This mismatch can be exploited by repeatedly calling the withdraw function: each call triggers a transfer of the same amount while the pendingWithdrawals entry remains unchanged, allowing an attacker to drain more tokens than they are legitimately owed. The impact is that users may see their balance appear correct on the UI – they receive a withdrawal as expected – but the protocol’s accounting becomes corrupted, leading to either locked funds that can never be reclaimed or a systematic loss of assets from the contract’s treasury. The issue manifests whenever the withdraw routine is executed, regardless of who calls it, and affects any participant that relies on the contract’s withdrawal mechanism, including regular users, liquidity providers, and the protocol’s overall financial health. It was discovered during a code review when a sponsor noted a similarity to a previously reported bug where the same function failed to reduce the pendingWithdrawals counter, linking the two findings together. The problem is subtle because the outward behavior (a successful transfer) seems normal, and there is no immediate error or revert; the faulty state persists quietly in storage, making it difficult to detect without audit or detailed state inspection. To remediate the issue, the withdraw function must follow a proper Checks‑Effects‑Interactions pattern: after confirming the user’s entitlement, it should first deduct the withdrawn amount from the pendingWithdrawals record and then transfer the tokens. This ensures that the contract’s internal accounting stays consistent with the actual token balances and prevents repeated extraction of the same funds.

## Recommendation
No recommendation
