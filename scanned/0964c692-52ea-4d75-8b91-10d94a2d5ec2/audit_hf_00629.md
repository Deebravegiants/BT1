# [M] M-06 | Add And RemoveLiquidity Orders Are Missing Slippage Checks

## Summary
Severity: Medium
Contest weight: 0.1103
Dataset id: 2130
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a Liquidity Order is placed there is no way for the caller to specify a minimum acceptable output amount. In typical AMM or liquidity pool scenarios, a user will include a minAmountOut parameter to protect themselves from adverse price movements or sandwich attacks that may occur between the placement of the order and the fulfilment. Without this parameter, the liquidity providers are subject to price changes and certain actions that can occur between the placement of their order and the fulfilment and therefore the liquidity provider could receive far fewer tokens (in the case of removing liquidity) or far fewer shares (in the case of adding liquidity) than they would expect under stable conditions.

## Recommendation
Consider adding a minAmountOut parameter to the LiquidityOrderParams struct.
