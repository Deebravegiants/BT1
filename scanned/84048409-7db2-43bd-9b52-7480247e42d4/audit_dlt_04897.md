# [M] [Tomo-M1] Can be overwritten the value of bulls and bears

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/70
Type: sherlock-finding

## Details
Tomo

medium

# [Tomo-M1] Can be overwritten the value of bulls and bears

## Summary

Can be overwritten the value of bulls and bears

## Vulnerability Detail

The value of bears, bulls, and matchOrders stores as a mapping with contractId.

This contractId decide by this function

```solidity
function hashOrder(Order memory order) public view returns (bytes32) {
        bytes32 orderHash = keccak256(
            abi.encode(
                ORDER_TYPE_HASH,
                order.premium,
                order.collateral,
                order.validity,
                order.expiry,
                order.nonce,
                order.fee,
                order.maker,
                order.asset,
                order.collection,
                order.isBull
            )
        );

        return _hashTypedDataV4(orderHash);
    }
```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/70_
