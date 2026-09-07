# [M] [Tomo-M4] Should transfer ETH if order.asset is WETH

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/73
Type: sherlock-finding

## Details
Tomo

medium

# [Tomo-M4] Should transfer ETH if order.asset is WETH

## Summary

Should transfer ETH if order.asset is WETH

## Vulnerability Detail

In the `matchOrder()`, if `order.asset` is `WETH`, users have to pay ETH 

```solidity
if (msg.value > 0) {
      require(msg.value == takerPrice, "INVALID_ETH_VALUE");
      require(order.asset == weth, "INCOMPATIBLE_ASSET_ETH_VALUE");

      WETH(weth).deposit{value: msg.value}();
  } else if(takerPrice > 0) {
```

However, in the `settleContract()`, there is no handling when the `order.asset` is WETH so users have to unwrap the WETH to ETH by themselves.

Many users may receive WETH directly and not know how to change it to ETH. Also, most users would expect to receive ETH because they paid ETH as `order.asset`.

Therefore, not handling WETH leads to making the user experience very poor

## Impact

Not handling WETH leads to making the user experience very poor

## Code Snippet

[https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L348-L352](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L348-L352)

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/73_
