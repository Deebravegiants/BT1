# [H] User can't withdraw from auction when number of sold contracts bigger than totalContracts

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/62
Type: sherlock-finding

## Details
Trumpero

high

# User can't withdraw from auction when number of sold contracts bigger than totalContracts

## Lines of code
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L312-L335

## Summary
User can't withdraw because forgetting to check `totalContractsSold` is bigger `totalContracts` or not ?  

## Vulnerability Detail
Function `_previewWithdraw` check if `totalContractsSold + data.size` is bigger than `auction.totalContracts` or not. If true it will increase `fill` amount by the difference between `auction.totalContracts` and `totalContractSolds` and `refund` amount will be increased by the remaining. 
```solidity=
// url = https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L312-L322
if (
    totalContractsSold + data.size >= auction.totalContracts
) {
    // if part of the current order exceeds the total contracts available, partially
    // fill the order, and refund the remainder
    uint256 remainder =
        auction.totalContracts - totalContractsSold;

    cost = lastPrice64x64.mulu(remainder);
    fill += remainder;
} 
```
But this updatation is just true when `auction.totalContracts >= totalContractsSold`. For the case when `auction.totalContracts < totalContracsSold`, this function will revert because of underflow issue. 


**For example**
* Auction has `totalContracts = 10`
* Alice buy 3 contracts with price = `maxPrice`
* Bob buy 8 contracts with price = `maxPrice`
* Candice buy 1 contracts with price = `maxPrice`

When the auction end, Candice calls `withdraw(0)` to get her refund (cause Alice and Bob will win all the contracts). But when function `withdraw()` call to function`_previewWithdraw` it will reverted. Here is the detail of for loops in function `_previewWithdraw`

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/62_
