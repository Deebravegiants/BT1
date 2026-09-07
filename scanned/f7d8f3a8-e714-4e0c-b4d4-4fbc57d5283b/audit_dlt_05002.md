# [M] WithdrawPeriphery.sol#L74-L77, DnGmxBatchingManager.sol#L152-L156 : maximum cap check is missed while setting the slippageThreshold

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/74
Type: sherlock-finding

## Details
ak1

medium

# WithdrawPeriphery.sol#L74-L77, DnGmxBatchingManager.sol#L152-L156 : maximum cap check is missed while setting the slippageThreshold

## Summary
Inside WithdrawPeriphery.sol, function `setSlippageThreshold` is used by admin to set the `slippageThreshold`. But this lacks to check whether the set value is exceedign or equal to the `MAX_BPS` 

## Vulnerability Detail

`slippageThreshold` is used to decide the `minTokenOut` in [line ](https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/periphery/WithdrawPeriphery.sol#L157).

If the `slippageThreshold` is equal to MAX_BPS , then the `minTokenOut` will be zero.

or 

if `slippageThreshold > MAX_BPS', the function [_convertToToken](https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/periphery/WithdrawPeriphery.sol#L147) could revert due to flow.

## Impact

If the `slippageThreshold` is equal to MAX_BPS , then the `minTokenOut` will be zero.

or 

if `slippageThreshold > MAX_BPS', the function [_convertToToken](https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/periphery/WithdrawPeriphery.sol#L147) could revert due to flow.

setting `slippageThreshold =   MAX_BPS` will impact in following functions, where `_convertToToken` is called.
https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/periphery/WithdrawPeriphery.sol#L113-L145

## Code Snippet

https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/periphery/WithdrawPeriphery.sol#L74-L77



https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxBatchingManager.sol#L152-L156


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/74_
