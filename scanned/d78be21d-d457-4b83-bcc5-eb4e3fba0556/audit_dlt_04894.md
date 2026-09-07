# [M] [Tomo-M5] Users can use the same nonce

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/74
Type: sherlock-finding

## Details
Tomo

medium

# [Tomo-M5] Users can use the same nonce

## Summary

Users can use the same nonce 

## Vulnerability Detail

In the `checkIsValidOrder` and `checkIsValidSellOrder` checks, the nonce is valid but this check doesn’t work for some reason.

1. The nonce doesn’t need to be bigger than the previous nonce

```solidity
require(order.nonce >= minimumValidNonce[order.maker], "INVALID_NONCE");
```

```solidity
require(sellOrder.nonce >= minimumValidNonceSell[sellOrder.maker], "INVALID_NONCE");
```

1. There is no setting after checking nonce

Therefore, the `checkIsValidOrder` and `checkIsValidSellOrder` don’t work correctly.

## Impact

The `checkIsValidOrder` and `checkIsValidSellOrder` don’t work correctly.

## Code Snippet

[https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L745](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L745)

```solidity
require(order.nonce >= minimumValidNonce[order.maker], "INVALID_NONCE");
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/74_
