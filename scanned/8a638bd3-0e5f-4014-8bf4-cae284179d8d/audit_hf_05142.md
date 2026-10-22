# [M] when ReserveBase undercollateralized ,Man-

## Summary
Severity: Medium
Contest weight: 0.5600
Dataset id: 23192
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Manager.sol does not take into account that reserve.redeemPrice may be less than 1:1 The current code, reserve.redeem(amount) followed by a direct transfer of the same USDC, will fail because it results in an insufficient balance and the order will not be triggered successfully
in Manager.sol:219
If balance order.interfaceFee.unwrap=true, need to convert DSU to USDC Use reserve.redeem(amount); But this method, in the case of undercollateralized, is possible to convert less than amount, but the current code implementation logic directly uses amount.
```solidity
/// @inheritdoc IReserve
// if overcollateralized, cap at 1:1 redemption / if undercollateralized, redeem pro-rata
}
reserve.redeem(amount);
}
```
Internal pre-conditions
External pre-conditions
1. XXXReserve.sol undercollateralized
Attack Path
1. alice place TriggerOrder[1] = {price < 123 , interfaceFee.unwrap=true}
2. XXXReserve.sol undercollateralized , redeemPrice < 1:1
3. when price < 123 , Meet the order conditions
4. keeper call executeOrder(TriggerOrder[1]) , but execute fail because revert Insufficient balance

## Recommendation
```solidity
reserve.redeem(amount);
}
```
