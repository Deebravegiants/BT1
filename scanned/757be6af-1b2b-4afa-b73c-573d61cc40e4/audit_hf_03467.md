# [M] GSU-1 | Incorrect Decrease Gas Estimation

## Summary
Severity: Medium
Contest weight: 0.0399
Dataset id: 18890
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an off‑by‑one error in the gas‑estimation routine used for decrease orders. When the contract builds the gas limit for a decrease order it calls estimateExecuteDecreaseOrderGasLimit and adds a constant of 1 to the variable gasPerSwap instead of adding the extra unit to the total number of swaps that will be performed. Decrease positions that require an additional swap because of the decreasePositionSwapType therefore have one swap less gas accounted for. The root cause is a misinterpretation of the extra swap as a per‑swap cost rather than an additional swap count. An attacker does not need to exploit the bug directly; any user who submits a decrease order will experience a transaction that may run out of gas and revert because the estimated gas limit is lower than the actual consumption. The impact is that the decrease operation fails, the user’s position remains unchanged, and the gas spent on the failed transaction is lost. This situation occurs only when a decrease order triggers the special swap type, i.e., when the protocol must execute an extra swap to unwind the position. Affected parties are end‑users who attempt to reduce or close positions and the protocol itself, which may appear unreliable or experience denial‑of‑service for decrease actions. The issue was discovered during a manual audit of the GMX Synthetics contract where the gas‑estimation logic was examined and the off‑by‑one was identified. Because gas estimation is an internal helper, the problem can be hard to notice until a transaction repeatedly fails with an out‑of‑gas error despite seemingly sufficient gas limits. From the user’s perspective the UI may show a decrease request submitted, but the transaction reverts and the user receives no refund or position change, often seeing a “out of gas” error and a loss of the gas fee. The bug belongs to the class of gas‑estimation errors where the formula does not correctly account for all execution steps, leading to under‑allocation of gas. To fix the issue the estimator should increase the swap length by one (or otherwise add the extra swap to the total gas calculation) instead of incrementing gasPerSwap, ensuring the gas limit covers the additional swap required by decreasePositionSwapType.

## Recommendation
Add 1 to the order’s swap length rather than the gasPerSwap.
