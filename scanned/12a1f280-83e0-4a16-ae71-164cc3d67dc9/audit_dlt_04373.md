# [H] A staker can make sure that no one will be able to write off the debt with his locked stake.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/105
Type: sherlock-finding

## Details
CodingNameKiki

high

# A staker can make sure that no one will be able to write off the debt with his locked stake.

## Summary
A staker can make sure, that no one will be able to call the function `debtWriteOff` in the UserManager contract after 
`block.number > lastRepay + overdueBlocks + maxOverdueBlocks`
As result the borrower's debt can't be written off using the stakers locked stake. 
The only way for the debt to be gone is if the borrower repays it back to the staker.

When the staker sees that the time is getting closer for the function `debtWriteOff` to be public and the borrower won't be able to pay it back in time. The staker can perform the issue described in `Vulnerability Detail`, so other users won't be able to write off the debt using his locked stake. 

## Vulnerability Detail
As for the example, we have two people Kiki and Jake:
Kiki has a stake of 10 000 Dai, he trusts Jake so he vouches the 10 000 Dai to him.
Jake successfuly borrowed the amount, as a result Kiki's stake of 10 000 Dai is locked.

Time passes and so far Jake repaid only 5 000 Dai back, as the time is getting closer for the function `debtWriteOff` to be public in the contract UserManager. Kiki understands that Jake won't be able to repay back the full loan in time.

https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/user/UserManager.sol#L726-L788

Kiki doesn't want to lose his stake, by someone writing off the debt. So he unstakes the repaid amount by Jake and calls the function `debtWriteOff` in the AssetManager contract and writes off out of his stake balance Jake's unpaid debt of 5 000 Dai. 
The outcome of this will look like this:

`balances[msg.sender][token] -= amount;` => `5 000 -= 5 000` => `balances[msg.sender][token] = 0`

After this actions Kiki will have zero amount left in the mapping `balances` allocated in AssetManager.

https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/asset/AssetManager.sol#L374-L378

As a result when people try to call the function `debtWriteOff` in the UserManager contract to write off the debt. 
It will revert because the function calls `debtWriteOff` in AssetManager to subtract the debt amount from Kiki's balance.
And since Kiki's balance is zero, the function `debtWriteOff` in UserManager will always revert.

https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/user/UserManager.sol#L782


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/105_
