# [H] Trader can bypass the `_is_liquidatable` by directly calling the `_full_close`

## Summary
Severity: High
Reporter: 0xpinky
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L206
Type: audit-issue

## Details
# Trader can bypass the `_is_liquidatable` by directly calling the `_full_close`

## Summary

`_is_liquidatable` is bypassed by  directly calling the _full_close.

## Vulnerability Detail

trader can call the following functions to close the trade either fully or partially from `MarginDex.vy`

1. [close_trade](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L206)
2. [partial_close_trade](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L256)

the above function would call the [close_position ](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L227) and [reduce_position ](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L290)functions from vault.vy.

when there is check for [_is_liquidatable](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L301) for reduce_position, but the same is missing in close_position

## Impact

trader can bypass liquidation check and fully close the trade.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L252

## Tool used

Manual Review

## Recommendation

Add [this ](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L301) check to [close_position ](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233-L279)as well.
