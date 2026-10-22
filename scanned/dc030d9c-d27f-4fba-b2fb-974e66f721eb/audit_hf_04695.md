# [M] LendingPool#flashAction is broken when try-

## Summary
Severity: Medium
Contest weight: 0.5663
Dataset id: 22465
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When refinancing an account, LendingPool#flashAction is used to facilitate the transfer. However due to access restrictions on updateActionTimestampByCreditor, the call made from the new creditor will revert, blocking any account transfers. This completely breaks refinancing across lenders which is a core functionality of the protocol. LendingPool.sol#L564-L579
```solidity
IAccount(account).updateActionTimestampByCreditor();
asset.safeTransfer(actionTarget, amountBorrowed);
{
    uint256 accountVersion = IAccount(account).flashActionByCreditor(actionTarget, actionData);
    if (!isValidVersion[accountVersion]) revert LendingPoolErrors.InvalidVersion();
}
```
We see above that account#updateActionTimestampByCreditor is called before flashActionByCreditor. AccountV1.sol#L671
```solidity
function updateActionTimestampByCreditor() external onlyCreditor updateActionTimestamp { }
```
When we look at this function, it can only be called by the current creditor. When refinancing a position, this function is actually called by the pending creditor since the flashaction should originate from there. This will cause the call to revert, making it impossible to refinance across lendingPools. Refinancing is impossible.

## Recommendation
Account#updateActionTimestampByCreditor() should be callable by BOTH the current and pending creditor.
