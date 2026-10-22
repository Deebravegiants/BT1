# [C] CRT-1 Transactions frontrunning

## Summary
Severity: Critical
Contest weight: 0.6057
Dataset id: 214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The code in this line contains an error in calculation
in line: FeeCollector.sol#L360
```solidity
uint256 returnAmount = amount * tokenBalance / value(erc20);
```
According to the formula, it is fixed price for the rest of tokenBalance or whole
amount, not the price for unit.
*Example:
Someone(something) makes updateReward for 10 WETH - user1
Let's assume now we have minimal price after a long period of time
Current price is 100 Inch for 10 WETH
user2 and user3 are atackers
User4 wants to make a full trade. He wants to buy 10 WETH for 100 1Inch. He wants make
a transaction
attacker puts the next transaction before User4
User2 updateReward with ~101010 WETH
the price is changed
User3 trades after User2 ~101010.mul(price)
User2 executes trade
attacker has a profit equal ~1.4 WETH
User4 got ~8.6 WETH. 1.4 WETH less that expected*
*Example 2
Let's assume, now we have minimal price after a long period of time
Someone(something) makes updateReward for 10 WETH - user1
Current price is 100 Inch for 10 WETH
User2 and User3 want to make partial trade. They want to buy 5 WETH for 50 1Inch. They
make a transaction at approximately the same time
User2 trades first and gets 5 WETH and spends ~50 1Inch. OK
User3 trades after User 2.5WETH and spends ~50 Inch. Not correct
User1 never gets his 1Inch because User3 or nobody wants to make this incorrect
transaction
In case User3 makes transaction for 5 WETH and ~spends 100 1Inch, User1 will receive
~2 times more 1Inch than excpected*

## Recommendation
Implement correct returnAmount calculation
2.2 MAJOR
Not Found
