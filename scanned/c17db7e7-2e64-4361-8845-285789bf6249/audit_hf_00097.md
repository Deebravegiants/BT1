# [M] FeeTaker is incompatible with fee-on-transfer tokens

## Summary
Severity: Medium
Contest weight: 0.5521
Dataset id: 176
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a fee-on-transfer token is used as a taker asset, the FeeTaker.sol contract receives takingAmount - tokenFee. This can cause the contract to revert because it assumes that the entire takingAmount is available on its balance.
```solidity
function postInteraction(
    IOrderMixin.Order calldata order,
    bytes calldata /* extension */,
    bytes32 /* orderHash */,
    address /* taker */,
    uint256 /* makingAmount */,
    uint256 takingAmount,
    uint256 /* remainingMakingAmount */,
    bytes calldata extraData
) external {
    ---SNIP---
    unchecked {
        IERC20(order.takerAsset.get()).safeTransfer(receiver, takingAmount - fee);
    }
}
```

## Recommendation
Validate the balance before transferring to the recipient
```solidity
function postInteraction(
    IOrderMixin.Order calldata order,
    bytes calldata /* extension */,
    bytes32 /* orderHash */,
    address /* taker */,
    uint256 /* makingAmount */,
    uint256 takingAmount,
    uint256 /* remainingMakingAmount */,
    bytes calldata extraData
) external {
    uint256 balance = IERC20(order.takerAsset.get()).balanceOf(address(this));
    if (balance < takingAmount) takingAmount = balance;
    ---SNIP---
}
```
