# [H] Possible overflow in `_payOutFirstInQueue`

## Summary
Severity: High
Contest weight: 0.7352
Dataset id: 19484
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** In `_payOutFirstInQueue()`, possible revert during `operatorTokenToDataInverse()`.

```solidity
uint amountOperatorTokens = moduleCall(address(exchangeRatePolicy), abi.encodeWithSelector(exchangeRatePolicy.operatorTokenToDataInverse.selector, amountDataWei));
```

If a delegator calls `undelegate()` with `type(uint256).max`, `operatorTokenToDataInverse()` will revert due to uint overflow and the queue logic will be broken forever.

```solidity
   function operatorTokenToDataInverse(uint dataWei) external view returns (uint operatorTokenWei) {
       return dataWei * this.totalSupply() / valueWithoutEarnings();
   }
```

** The queue logic will be broken forever because `_payOutFirstInQueue()` keeps reverting.

## Recommendation
** We should cap `amountDataWei` before calling `operatorTokenToDataInverse()`.
