# [H] Initialization to zero price can cause permanent stuck state due to clamping

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23437
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In ChainlinkOracle in the constructor, the contract initializes currentPriceX96, lastPriceX96, and
emaPrice using the current sqrtPriceX96 from the Uniswap V4 pool. If the pool is uninitialized (sqrtPriceX96 ==
0), all these price variables are set to zero. In this state, the update function will always clamp any new price to
the range lastPriceX96 ± (lastPriceX96 >> 6), which evaluates to 0 ± 0 = 0. As a result, the oracle is stuck
at zero and cannot update to a non-zero price, even if the pool becomes initialized later.
Impact: The oracle will be permanently stuck at a zero price if deployed before the pool is initialized. This prevents
the oracle from ever reflecting the true market price, breaking all dependent pricing and margin logic. Users and
protocols relying on the oracle will receive invalid (zero) price data, potentially causing loss of functionality or
incorrect behavior.

## Recommendation
Add a check in the constructor (and/or in the update function) to ensure that initialization only occurs if sqrtPriceX96 > 0. If the pool is uninitialized, revert deployment or defer initialization until a valid price is available. Alternatively, allow the oracle to update from zero to a non-zero price once the pool is initialized, bypassing the clamp logic when lastPriceX96 == 0.
