# [M] User get a wrong amount of shares when deposit to queue

## Summary
Severity: Medium
Reporter: Trumpero
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L103-L104
Type: audit-issue

## Details
# User get a wrong amount of shares when deposit to queue

## Lines of code 
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L103-L104

## Summary
There are ERC20 tokens that may make certain customizations to their ERC20 contracts.
One type of these tokens is deflationary tokens that charge a certain fee for every ```transfer()``` or ```transferFrom()```

## Vulnerability Detail
For example, I will assume that `ERC20` is deflationary token. After [line 103](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L103), the actual amount of `ERC20` that `Queue` gained will be smaller than `amount`, I will call it `amount2`. After [deposit call](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L104), user still get shares correspond to `amount` instead of `amount2`. 
When user call cancel and withdraw their `ERC20` back, it will burn `amount` share and get `amount-fee` ERC20. It will make user call `cancel` after lose their ERC20 because of not enough fund 

## Impact
User can't withdraw their `ERC20`

## Tool used
Manual Review

## Recommendation
Get the balance before transfer and balance after transfer of queue, and mint amount correspond to the difference.
