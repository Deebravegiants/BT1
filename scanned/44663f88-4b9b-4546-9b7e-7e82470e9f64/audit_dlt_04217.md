# [M] Lack of curPoolInfo.weight validation in DODORouteProxy.sol#DodoMultiswap

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/28
Type: sherlock-finding

## Details
ctf_sec

medium

# Lack of curPoolInfo.weight validation in DODORouteProxy.sol#DodoMultiswap

## Summary

Lack of curPoolInfo.weight validation in DodoMultiswap

## Vulnerability Detail

We set the total Weight in DODORouteProxy.sol#DodoMultiswap

```solidity
// in PoolInfo, pool weight has 8 bit, so totalWeight < 2**8
uint256 public totalWeight = 100;
```

this parameter is used inside the function DodoMultipswap, which calls _multiswap.

```solidity
uint256 curTotalWeight = totalWeight;
```

and

```solidity
uint256 curTotalAmount = IERC20(midToken[i]).tokenBalanceOf(assetFrom[i - 1]);
uint256 curTotalWeight = totalWeight;

// split amount into all pools if needed, transverse all pool in this split
for (uint256 j = splitNumber[i - 1]; j < splitNumber[i]; j++) {
    PoolInfo memory curPoolInfo;
    {
        (address pool, address adapter, uint256 mixPara, bytes memory moreInfo) = abi
            .decode(swapSequence[j], (address, address, uint256, bytes));

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/28_
