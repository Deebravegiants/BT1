# [M] M-04 | uiFee is Taken Twice During Shift

## Summary
Severity: Medium
Contest weight: 0.0313
Dataset id: 21420
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a double application of the protocol’s user interface fee (uiFee) during asingle shift operation that internally performs a deposit followed by a withdrawal. The root cause is that the fee logic is implemented in both the deposit function and the withdrawal function, and the shift routine calls these two functions sequentially without disabling one of the fee calculations. As a result, when a user initiates a shift expecting a single fee deduction, the contract deducts the uiFee twice – once on the deposit side and again on the withdrawal side. An attacker or any user can exploit this by repeatedly invoking the shift function, causing the protocol to over‑charge participants and effectively drain a small amount of value from each transaction. The impact is a reduction of the net amount received by the user; for example, a user who expects to receive 100 tokens after a shift may only receive 100 − 2 × uiFee, leading to missing balances, unexpected zero‑fee refunds, or overall lower returns. This condition occurs only when the shift operation is used, i.e., when deposit and withdrawal are combined in a single transaction, and it affects all participants who rely on the shift feature, including regular users, liquidity providers, and the protocol’s accounting layer. The issue was discovered during a manual audit that examined the fee handling paths and noticed that the same fee variable was subtracted in two consecutive internal calls. It can be hard to notice because the UI typically displays the fee amount once, and the double deduction is hidden in the contract’s internal accounting, making the discrepancy appear only in the final transferred amount. To remediate, the fee should be applied exactly once per shift – either by moving the uiFee calculation to the shift wrapper and disabling it in the underlying deposit or withdrawal, or by redesigning the shift to call a fee‑free internal transfer function. This correction restores the intended accounting invariant that the total fee charged per user action equals uiFee, preventing unintended loss of funds and preserving the protocol’s economic model.

## Recommendation
Include the uiFee on either the deposit or the withdraw, but not both.
