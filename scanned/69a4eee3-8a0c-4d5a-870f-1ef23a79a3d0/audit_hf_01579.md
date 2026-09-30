# [H] MJR-16 Looping a linked list

## Summary
Severity: High
Contest weight: 0.2579
Dataset id: 8469
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the line: AccountFactory.sol#L40 there's a linked list called _nextCreditAccount.
In this list, the account address refers to the address of the next account. Thus, a chain of addresses linked to each other is formed.
At the lines contracts/core/AccountFactory.sol#L248-L263 there's a takeOut() function.
It takes the credit account address from anywhere on the list and attaches it to the credit manager.
At the lines: AccountFactory.sol#L186-L199 there's a function returnCreditAccount(). It returns the credit account address in the tail of the _nextCreditAccount linked list.
In the takeOut() function there is no logic for checking and zeroing the link to the next account from the taken account address.
When the taken address is returned to the tail of the list, it will contain the old value of the address. Loop through the list may occur when the function _countCreditAccountsInStock() is used for the line: AccountFactory.sol#L352-L365.

## Recommendation
It is necessary to zero the next item from the linked list after the AccountFactory.sol#L260 line:
```solidity
_nextCreditAccount[creditAccount] = address(0);
```
