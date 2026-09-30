# [H] H-2 Overﬂow will entirely block the plugin

## Summary
Severity: High
Contest weight: 0.0697
Dataset id: 2901
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an integer overflow that occurs during the second initialization of a list inside the VolatilityOracle contract. When the contract attempts to re‑initialize the internal array or counter a second time, the arithmetic operation that increments the length or index wraps around the maximum uint256 value and resets to zero. This overflow is not guarded by any safety check, so the internal state becomes inconsistent and subsequent plugin updates that rely on the list fail silently. As a result, the volatility plugin can no longer push new data to the pool, effectively freezing the price‑feed mechanism. Users interacting with the pool notice that their balances do not change despite expected market movements, refunds are not issued, and the UI shows no new volatility information. The condition only manifests after the list has been initialized twice, a scenario that typical unit tests may not cover, making the bug hard to detect during development. The issue was uncovered during a manual security audit by MixBytes, which examined the initialization logic and identified the unchecked arithmetic as the root cause. Because the overflow corrupts the plugin’s state, only an admin‑only recovery function can reset the contract, meaning ordinary users cannot unfreeze the system themselves. The bug belongs to the class of unchecked arithmetic overflows that lead to state‑locking conditions, violating the protocol’s assumption that the plugin will always be able to accept new updates. To remediate, the contract should either prevent re‑initialization, reset the counter before a second use, or explicitly use an unchecked block only if the overflow is intentional and safely handled, but preferably incorporate overflow checks or SafeMath‑style guards to maintain correct accounting and ensure that plugin updates remain functional.

## Recommendation
We recommend using the unchecked block here since overﬂow is desired.
