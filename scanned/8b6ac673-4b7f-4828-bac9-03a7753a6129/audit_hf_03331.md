# [M] SWPU-1 | Lack Of Validation For Homogenous Markets

## Summary
Severity: Medium
Contest weight: 0.0433
Dataset id: 18182
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract implements a function validateReserve that checks that the reserve balance for the token being sent out (tokenOut) matches the expected amount. In markets where the short token and the long token are the same asset, the condition cache.tokenOut == _params.market.longToken is always true, so the function only validates the reserve for the long side. The short side is never inspected, leaving the contract with an unchecked reserve balance for the short position. This occurs because the code assumes tokenOut can be distinguished between long and short tokens, which is not true for homogeneous markets. An attacker can exploit this by creating a market where shortToken == longToken, then depositing or withdrawing tokens only on the short side, causing the contract’s internal accounting to diverge from the actual token balance. The mismatch can be used to trigger trades at manipulated prices, withdraw more assets than should be allowed, or cause the market to become insolvent. The impact is that users may see their expected refunds or trade outcomes disappear, balances may become zero or negative, and the protocol’s overall liquidity can be drained. The bug manifests whenever a market is instantiated with identical long and short tokens, which is allowed by the factory contract. Users, liquidity providers, and the protocol itself are affected because the accounting guarantees are broken. The issue was discovered during a manual audit that inspected the reserve‑validation logic and noticed the equality check does not differentiate the two token roles. It is subtle because the contract still compiles and works for normal markets, and the missing check does not raise an error until a homogeneous market is used, making it easy to overlook. The proper fix is to add explicit validation for both long and short reserves when the market’s tokens are identical, or to forbid creation of markets where shortToken equals longToken. In generic terms, this is a validation‑logic flaw that results from an assumption of token heterogeneity, leading to unchecked state and potential financial loss.

## Recommendation
For markets where the shortToken is the same as the longToken, be sure to validate the reserves for both longs and shorts.
