# [M] Only one action can be allowed

## Summary
Severity: Medium
Reporter: Jolly Hotpink Pig
Source: https://github.com/sherlock-audit/2023-07-blueberry/blob/main/blueberry-core/contracts/BlueBerryBank.sol#L298-L335
Type: audit-issue

## Details
# Only one action can be allowed
## Summary

Only one type of action can be allowed to be performed thought a contract at one moment. 

## Vulnerability Detail

The problem is that only one type of action can be performed at the moment.
For instance, Only Borrow allowed, OR only Repay allowed, OR only Lend Allowed etc.
So the owner cannot allow users to borrow and repay at the same time.

## Impact

Limitation users. The user cannot repay at any time. For instance, if the current state of the bank is set to a different phase. Which may lead to user liquidation

## Code Snippet

https://github.com/sherlock-audit/2023-07-blueberry/blob/main/blueberry-core/contracts/BlueBerryBank.sol#L298-L335

## Tool used

Manual Review

## Recommendation
Add separate "bankStatus" for each action
