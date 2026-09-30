# [M] Missing slippage protection for Stargate swap in OmnichainMessenger._distributeOrders()

## Summary
Severity: Medium
Contest weight: 0.0309
Dataset id: 13544
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a missing slippage protection on the Stargate swap that is performed inside the OmnichainMessenger._distributeOrders() function. The contract calls the Stargate router with the parameter that represents the minimum acceptable amount of the destination token (minAmountLD) hard‑coded to zero. Because the router is instructed to accept any amount, the swap can complete even when the actual received amount is far below the expected value or even zero. This occurs whenever the internal _distributeOrders() routine is executed, which the audit notes is only invoked by a trusted governance call. The root cause is the absence of a check that validates the output of the cross‑chain swap against a pre‑computed lower bound, effectively disabling the usual slippage guard that prevents adverse price movements. An attacker who can influence the Stargate pool price, for example by front‑running the transaction or by manipulating the liquidity, can cause the swap to return a reduced amount of tokens. Since the contract does not revert on a shortfall, it will record the order as fulfilled and forward the insufficient amount to the intended recipient. From a user’s perspective this manifests as a cross‑chain transfer that arrives with less than the expected balance, sometimes appearing as a zero balance or a missing refund, even though the transaction succeeded on‑chain. The impact is financial loss: users receive fewer assets than they paid for, the protocol’s accounting becomes inconsistent, and the overall trust in the messaging service is eroded. The issue was discovered during a manual code review when the auditor observed the explicit zero literal passed as the minAmountLD argument. It can be hard to notice because the transaction does not revert and no explicit error is emitted; only the downstream token balance reveals the discrepancy. To remediate the problem, the function should accept a minAmountLD value that is calculated off‑chain based on the quoted price and a reasonable slippage tolerance, and pass this value to the Stargate swap call. Enforcing a non‑zero minimum amount ensures that the swap will revert if the received amount falls below the expected threshold, thereby protecting user funds and preserving protocol accounting integrity.

## Recommendation
Since OmnichainMessenger._distributeOrders() is only called in a trusted context by the governance, it is possible to pass the minAmountLD values as a parameter to the function and to calculate it off-chain.
