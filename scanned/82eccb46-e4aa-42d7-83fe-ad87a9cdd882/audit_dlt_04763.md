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
* i = 0
    * `data.buyer = Alice`
    * `data.size = 3`
    * `totalContractsSold = 0 + 3 = 3` 
* i = 1
    * `data.buyer = Bob`
    * `data.size = 8`
    * `totalContractsSold = 3 + 8 = 11`
* i = 2
    * `data.buyer = Candice`
    * `data.size = 1`
    * `remainder = totalContracts - totalContractSolds = 10 - 11 = -1 < 0` --> revert here 

## Impact
User can't get either their refund premium or their long tokens 

## Code Snippet
```typescript=
const buyer1OrderSize = totalContracts.add(1); //.sub(totalContracts.div(10));
const buyer2OrderSize = totalContracts.sub(10);
const buyer3OrderSize = totalContracts.div(10).mul(2);

// buyer1 buy totalContracts + 1 contracts 
await asset
  .connect(signers.buyer1)
  .approve(addresses.auction, ethers.constants.MaxUint256);
await auction.addLimitOrder(epoch, maxPrice64x64, buyer1OrderSize);

// buyer2 buy totalContracts - 10
await asset
  .connect(signers.buyer2)
  .approve(addresses.auction, ethers.constants.MaxUint256);
await auction
  .connect(signers.buyer2)
  .addLimitOrder(epoch, maxPrice64x64, buyer2OrderSize);

// buyer2 call withdraw to get the refund --> revert 
await expect(auction.connect(signers.buyer2).withdraw(0)).to.reverted;
```
To check with test, u can use this file 
https://gist.github.com/Trumpero/575d1b3b035e2f8a4e104d1e6062c648
I write one more describe `::Bug` beside your original describe `::Auction` in file `Auction.behavior.ts` (just too lazy to write a new one). 

## Tool used
Hardhat 

## Recommendation
* Add more one more `if` condition when `totalContractsSold > auction.totalContracts`. For this case we will increase `refund` amount by `data.size`.
 
duplicate of #106
