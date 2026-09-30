# [M] Lowering the max leverage for a market will unfairly result in liquidated positions

## Summary
Severity: Medium
Reporter: Dug
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1504-L1509
Type: audit-issue

## Details
# Lowering the max leverage for a market will unfairly result in liquidated positions

## Summary

The `Vault` contract allows the admin to adjust the max leverage allowed for markets through the `set_max_leverage_for_market` function.

The issue is that reducing the max leverage for a market will invalidate protective stop loss orders and potentially make positions immediately vulnerable to liquidations.

## Vulnerability Detail

For traders to be able to protect their positions from liquidations, they are able to place take-profit and stop-loss orders. But to do so, they need assurances that the max leverage allowed for a market will not be reduced, otherwise their orders will be invalidated and their positions will be vulnerable to liquidations.

## Impact

Reducing the max leverage for a market will invalidate protective stop loss orders and potentially make positions immediately vulnerable to liquidations.

The protocol should not allow for this.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1504-L1509

## Tool used

Manual Review

## Recommendation
Only allow for increases in max leverage for a market.
