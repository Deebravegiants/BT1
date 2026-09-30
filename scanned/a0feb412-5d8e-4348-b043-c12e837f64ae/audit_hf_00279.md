# [H] `IndexTemplate.sol#compensate

## Summary
Severity: High
Contest weight: 0.0428
Dataset id: 1429
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a precision‑loss bug that occurs when the contract converts between a user's share balance and the underlying token amount that those shares represent. The root cause is the use of integer arithmetic without appropriate scaling or rounding, which truncates fractional values during the share‑to‑token and token‑to‑share calculations. Because the conversion is not mathematically reversible, each round‑trip loses a small amount of value. An attacker or any user can exploit this by repeatedly depositing tokens, converting them to shares, and then converting the shares back to tokens, thereby extracting the accumulated rounding error as extra underlying tokens, or by forcing honest participants to receive slightly less than they deposited. The impact manifests as missing or reduced refunds, balances that appear to shrink, or funds that seemingly disappear from the pool. This issue appears whenever the conversion functions are invoked, especially for small amounts or after many cycles of deposits and withdrawals, and it affects any party that holds shares – individual users, liquidity providers, and the protocol itself, because the total accounting of underlying assets becomes inconsistent. The problem was identified during a Code4rena security audit through mathematical analysis and test cases that exposed mismatched totals after back‑and‑forth conversions. The bug is hard to notice because the loss per operation is typically tiny and may only become apparent after many transactions, and the user interface may still show the correct nominal share balance while the underlying token accounting is off. To remediate the issue, the contract should employ fixed‑point arithmetic with a sufficiently large scaling factor, apply consistent rounding (e.g., round‑down on one direction and round‑up on the inverse), or store values as high‑precision integers and ensure that share‑to‑token and token‑to‑share functions are true inverses. In broader terms, this is a class of unit‑conversion precision errors that violate the business logic assumption that shares represent an exact proportional claim on the underlying assets, leading to accounting discrepancies and potential fund loss.

## Recommendation
No recommendation
