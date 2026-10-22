# [M] M-8 Fees applied twice

## Summary
Severity: Medium
Contest weight: 0.0269
Dataset id: 7101
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a double‑fee accounting error in the stable‑swap view logic. The contract already subtracts protocol fees when it calculates the base token amounts for a swap, but the getDyUnderlying view function applies the same fee a second time before returning the quoted output amount. This redundant deduction originates from the fee logic being invoked in two separate places: first in the core amount calculation and again in the helper view that is intended only to expose the result. Because the view function is often used by front‑ends and off‑chain services to display expected swap results, users are shown a lower output than they would actually receive if the fee were applied only once, or they may be over‑charged when the contract internally enforces the fee twice. An attacker does not need to exploit a low‑level reentrancy; the issue can be triggered simply by calling the public getDyUnderlying function with any token pair, causing the returned amount to be reduced by the fee twice. The impact is that traders and liquidity providers lose additional value on each swap – the protocol appears to charge higher fees than advertised, leading to “funds disappear” symptoms where a user expects to receive a certain amount of tokens but receives noticeably less, sometimes even zero if the fee percentage is high relative to the trade size. The condition occurs whenever the view function is used for price estimation or when a front‑end relies on its output for UI display, which is common in DeFi applications. The affected parties are any users interacting with the stable‑swap pool, as well as the protocol itself because the mis‑pricing can erode trust and reduce trading volume. The issue was discovered during a manual security audit that compared the fee handling in the core calculation with the logic in the view function and identified the redundant fee application. It can be hard to notice because the contract still executes successfully and the fee deduction is deterministic; only a careful review of the accounting flow reveals the double subtraction. The recommended remediation is to remove the fee deduction from the getDyUnderlying function, ensuring that fees are applied exactly once in the base calculation, thereby aligning the quoted output with the actual amount transferred and restoring correct accounting semantics.

## Recommendation
We recommend removing fees applying in the getdyunderlying function.
