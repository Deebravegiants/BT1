# [H] Price manipulation risk on auctions due to precision loss possibilities.

## Summary
Severity: High
Reporter: sheys
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122
Type: audit-issue

## Details
# Price manipulation risk on auctions due to precision loss possibilities.

## Summary
Price could underflow and result close to the max value of an unsigned integer..

## Vulnerability Detail
In the code piece in [L122](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122):

``` solidity
uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```
The code logic can cause price manipulation risk as the arrangement of the maths can cause precision loss and lead to the underflow/overflow of the price result.

Let's expand on this, consider a situation where we have the following values:
``` solidity
startPrice of NFTs = 5e18
endPrice of NFTs = 1e18

startTime = 86400 (1 day/24 hrs)

endTime = 3600 (1 hr)

```
Now with,  ```uint256 timePassed = time - startTime;```, if current block.timestamp is 90000,
We'll have: 
```solidity 90000 - 86400 = 3600```

Going further...
``` solidity
        uint256 totalSteps = (endTime - startTime) / stepSize;

(82800/24 = 3450)

        uint256 currentStep = timePassed / stepSize;

(3600/24 = 150)

        uint256 priceRange = startPrice - endPrice;

(5e18 - 1e18 = 4e18)

uint256 price = startPrice - (priceRange * currentStep / totalSteps);

5e18 - ( 4e18  * 150 /24)

500 - 2.4e19

= - 2.39e19
```

## Impact

-2.3e19 would underflow to the larger value of uint256 type at around:  2**256 - 2.3e19

This will max out the value of price and inflates the price as well as drain out the user of their funds

## Code Snippet

``` solidity
uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```

## Tool used
Manual Review

## Recommendation
Solidity executes divisions before multiplication so it is good practice to declare logics differently. For example:

``` solidity
uint256 price = startPrice - (priceRange * currentStep) / totalSteps;
```
So that it does multiplication first before division.
