# [M] Incorrect withdrawal requested

## Summary
Severity: Medium
Contest weight: 0.5552
Dataset id: 13362
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a logical error in the withdrawal request routine of a staking contract that interacts with the Tokemak pool. The contract calculates the amount it can actually withdraw (amountToRequest) as the lesser of the user's current balance and the amount supplied by the caller (_amount). This calculation correctly handles the case where the balance is smaller than the requested amount, such as when a user invokes an unstakeAllFromTokemak operation. However, instead of passing the computed safe value (amountToRequest) to the external Tokemak pool’s requestWithdrawal function, the contract mistakenly forwards the original caller‑supplied _amount. When balance < _amount, the contract therefore asks the pool to withdraw more tokens than it holds. This mismatch can cause the external call to revert, leave the withdrawal request in an inconsistent state, or result in the user receiving less than expected. The impact is that users attempting to withdraw their funds may see zero or reduced tokens returned, experience failed transactions, or have their balances appear unchanged, effectively locking their assets. The condition occurs only when the internal balance is lower than the amount parameter, a scenario that is exercised during full unstake calls but may be rarely tested, making the bug hard to notice. The issue was discovered during a Code4rena audit by reviewing the _requestWithdrawalFromTokemak function’s logic. The problem exemplifies a common class of bugs where an incorrect variable is used as an argument to an external contract call, leading to parameter misuse and accounting violations. From a user’s perspective, the expected behavior—receiving the full requested withdrawal—does not occur; instead the UI may show a successful request while the actual token transfer is zero or incomplete, breaking trust in the platform. To remediate, the contract should replace the erroneous argument with the safe amountToRequest, ensuring that the requestWithdrawal call never asks for more than the contract’s available balance, thereby aligning the withdrawal logic with the financial accounting assumptions of the protocol.

## Proof of Concept
1. In _requestWithdrawalFromTokemak function, amountToRequest is calculated as

```solidity
// the only way balance < _amount is when using unstakeAllFromTokemak
uint256 amountToRequest = balance < _amount ? balance : _amount;
```

2. Now assuming balance < _amount then amountToRequest becomes balance
3. But tokePoolContract.requestWithdrawal is called over _amount instead of amountToRequest which means withdrawal is requested over an extra amount

## Recommendation
Modify Staking.sol#L326 to

```solidity
if (amountToRequest > 0) tokePoolContract.requestWithdrawal(amountToRequest);
```
