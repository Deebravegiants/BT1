# [H] `matchOrder` does not validate for valid prices (collateral , premium )

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/69
Type: sherlock-finding

## Details
ak1

high

# `matchOrder` does not validate for valid prices (collateral , premium )

## Summary

`matchOrder` does not validate for valid prices (collateral , premium )
placing order without valid price could hurt any one of the user either buyer or seller.

## Vulnerability Detail

For `matchorder` in following line of codes [Line](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L348-L359), `makerPrice` and `takerPrice` are transferred to the contract without checking whether they are valid price value. 

unfortunately the [checkIsValidOrder](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L734-L761) also does not have any protection from reverting invalid price values.

## Impact

matching order without valid price will hurt both buyer and seller.

Lets say.. if bull placing order without any collateral, the order will be matched and settled when the time reached.

Even in [settleContract](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L402-L406) the bear will receive only if the `bearAssetAmount` is greater than zero.

At times, bull will take without paying any collateral. The bearer will receive his premium amount only.

## Code Snippet

https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L306-L367

## Tool used

Manual Review

## Recommendation

Check for valid premium and collateral amount while validating order [checkIsValidOrder](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L734-L761)
