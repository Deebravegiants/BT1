# [C] ORDM-1 | Attacker Can Drain OrderManager

## Summary
Severity: Critical
Contest weight: 0.5891
Dataset id: 20572
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating an order with the function createNewPosition(), a user can send an executionFee to the feeReceiver. The feeReceiver is different from the orderManager, meaning the executionFee will not be in the orderManager. When cancelling an order the executionFee is returned to the user:
```solidity
if (userOrder.executionFee != 0) {
    userBalance = userBalance + userOrder.executionFee;
}
...
if (userBalance != 0) {
    IERC20(market.depositToken).safeTransfer(userAddress, userBalance);
}
```
An attacker can create a order with a large execution fee and then cancel that order. By doing so, they can drain the orderManager as the orderManager is the one paying the refund, while the original funds are with the feeReceiver. `_closePosition()`, `_decreasePosition()`, `_increasePosition()`, `_liquidatePosition()` will no longer fully work as all of these functions will eventually transfer the collateral either back to the user or to the vault. However, due to this attack the orderManager will not have sufficient funds to cover these transactions as it will have zero collateral.

## Recommendation
Either do not refund the executionFee to the users or leave the executionFee in orderManager until settlement occurs. At that point, the keeper can pull the executionFee.
