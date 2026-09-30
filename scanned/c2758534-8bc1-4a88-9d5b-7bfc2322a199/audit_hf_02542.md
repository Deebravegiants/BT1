# [M] ZeroExAdapter cannot process orders with sellCurrency == localBuyCurrency

## Summary
Severity: Medium
Contest weight: 0.0334
Dataset id: 13543
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the ZeroExAdapter contract, which is the sole implementation of the phutureOnConsumeCallbackV1 function used by the Phuture protocol. When an outgoing order is constructed such that the sellCurrency field is identical to the localBuyCurrency field – meaning the same token is being sold and bought on the same chain – the adapter attempts to transfer the remaining balance to the order recipient by calculating params.currencyOut.balanceOfSelf() minus the balance recorded before the callback (balanceBefore). Because the token being transferred is the same as the one held by the contract, the balance before the callback already includes the amount that should be sent, resulting in a subtraction that yields zero. Consequently, no tokens are transferred to the recipient, the slippage check in the OrderBook fails, and the order appears to have been processed without delivering the expected funds. This situation can be triggered by either a mis‑configured order or a deliberately crafted order that exploits the assumption that sellCurrency and buyCurrency are always different. Users experience a silent failure: the UI may indicate that the order succeeded, yet the expected refund or token receipt is missing, leading to confusion and potential loss of funds. The issue was uncovered during a systematic audit of the Phuture V2 contracts, where the auditors observed that the callback logic did not account for the edge case of identical currencies. The bug is subtle because the transfer call does not revert; it simply sends zero value, making the failure hard to detect without explicit balance checks. To remediate the problem, the adapter should include a guard that detects when sellCurrency equals localBuyCurrency and either prevents such orders or adjusts the transfer logic to correctly handle the same‑currency scenario, for example by using the explicit amountOut parameter instead of a balance difference calculation. In broader terms, this is a classic case of an accounting mismatch caused by an incorrect assumption about token distinctness, leading to a refund calculation error that violates the protocol’s financial guarantees.

## Recommendation
No data
