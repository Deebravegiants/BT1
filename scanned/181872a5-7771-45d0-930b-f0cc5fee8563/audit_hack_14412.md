# [M] Users who mint in an auction, in which priceRange * currentStep < totalSteps will get charged more than expected

## Summary
Severity: Medium
Reporter: OxZ00mer
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122
Type: audit-issue

## Details
# Users who mint in an auction, in which priceRange * currentStep < totalSteps will get charged more than expected

## Summary
Users who mint in an auction, in which ``priceRange * currentStep < totalSteps``  will get charged the startPrice instead of the current price, because of a bad division operation.

## Vulnerability Detail
The auction allows for``startPrice`` and``endPrice`` to be set in the constructor. In a scenario where ``startPrice``and ``endPrice `` are very close in value and the total steps are very frequent the minters, who mint during the time when ``priceRange * currentStep < totalSteps`` will get charged the ``startPrice`` instead of the supposed current price.

Consider the following scenario:
```md
startPrice = 1e18
endPrice = 999999999999900000
priceRange = 1e5

length = 2592000 seconds // 30 days
stepSize = 12 seconds // 1 block on average
totalSteps = 216000
```

The following test demonstrates how the first two steps have the startPrice instead of a different one.
```solidity
    function logDetails() public {
        console.log("startPrice", START_PRICE);
        console.log("currentPrice", auction.getPrice());
        console.log("difference", START_PRICE - auction.getPrice());
        console.log("currentStep", (block.timestamp - startTime) / 12);
        console.log("\r");
    }

    function testIncorrectPrice() public {
        vm.warp(startTime);
        for (uint i; i < 10; ++i){
            if (i < 3) console.log("startPrice at step", i);
            else console.log("normal price at step", i);
            logDetails();
            vm.warp(startTime + 12 * (i + 1));
        }
    }
```

In this specific scenario, the minters in the first 2 steps(blocks) will get the ``startPrice`` instead of their respective lower prices.

```solidity
// @audit the  (priceRange * currentStep / totalSteps) will equate to 0 in this case:
uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```

## Impact
The minters in the first few steps will get a slightly worse price than expected.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122


## Tool used

Manual Review

## Recommendation
Add some minimum ``priceRange`` value check in the constructor.
