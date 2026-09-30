# [H] MJR-12 Impossible liquidity removing

## Summary
Severity: High
Contest weight: 0.0151
Dataset id: 8465
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns a liquidity pool contract that becomes unable to return assets to users when the pool’s capital is almost entirely borrowed. The root cause is an accounting mismatch: the contract assumes that the on‑chain token balance (balanceOf(address(this))) is always sufficient to cover a user’s withdrawal request (amountSent). When a large portion of the pool’s funds are lent out, the on‑chain balance drops below the amount a user tries to withdraw, causing the condition amountSent > balanceOf(address(this)) and the transaction to revert. This situation can be triggered by a malicious borrower who deliberately drains the pool’s available liquidity, effectively locking other users’ funds and creating a denial‑of‑service scenario. From a user’s perspective the symptom is that a withdrawal or liquidity removal transaction fails, the UI shows an error or simply does not complete, and the user sees no tokens returned despite having a positive balance in the protocol. The impact is that legitimate liquidity providers may be unable to retrieve their capital, leading to funds being effectively frozen and eroding trust in the protocol. The issue was discovered during a formal security audit performed by MixBytes, and it is subtle because it only manifests under extreme borrowing conditions that may not be exercised in routine testing. The bug belongs to the class of “liquidity‑locking” or “insufficient‑reserve” defects, where the contract’s business logic does not enforce a minimum reserve or provide a fallback path for withdrawals when the internal balance is insufficient. To remediate the problem the contract should implement a safe‑exit mechanism, such as a function that allows the protocol to close an account and force‑return the remaining assets to liquidity providers, or enforce borrowing limits that guarantee a reserve sufficient to satisfy any pending withdrawal request. By ensuring that either the borrowed amount can be reclaimed before a withdrawal or that a fallback path exists, the protocol can avoid the situation where users expect a refund but receive zero, and the accounting invariants of the pool remain intact.

## Recommendation
We recommend adding a function for closing some account to return funds to LP.
