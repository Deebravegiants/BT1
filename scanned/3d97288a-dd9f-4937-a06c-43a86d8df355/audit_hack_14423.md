# [M] High priceRange and step ranges can cause integer overflows

## Summary
Severity: Medium
Reporter: jboetticher
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L116-L122
Type: audit-issue

## Details
# High priceRange and step ranges can cause integer overflows

## Summary
If the range between `startPrice` and `endPrice` is too large or if the range between `startTime` and `endTime` is too large, an integer interflow can occur in the `getPriceAt(uint256 time)` function.

## Vulnerability Detail

A user may opt to use a very large startPrice and a very low endPrice with a reasonable end and start time frame. For example, 

```solidity
        uint256 time = 17678016;
        uint256 startTime = 17677016;
        uint256 endTime = 17678017;
        uint256 startPrice = 1000000000000000000000000000000000000000000000000000000000000000000000000000;
        uint256 endPrice = 0;
```

When the following line of code within `getPriceAt(uint256 time)` is ran, an integer overflow occurs because the priceRange * currentStep is greater than the max value of uint256. This makes a mint impossible:

```solidity
 uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```

The same issue can occur if the time range is too large and the current block is extremely high, but this is unlikely to happen unless Ethereum MainNet somehow gets block speeds of 1ms.  

## Impact

Impossible for users to mint

## Code Snippet

```solidity
        uint256 timePassed = time - startTime;
        uint256 totalSteps = (endTime - startTime) / stepSize;
        uint256 currentStep = timePassed / stepSize;
        uint256 priceRange = startPrice - endPrice;

        // multiplication can cause integer overflow

        // Calculate the price at the current step
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L116-L122

## Tool used

Manual Review
Forge fuzzing

## Recommendation

To keep functionality, use a big number math solution such as linked lists of uint256.  
Easiest solution is to remove functionality by putting limits on the price and steps. But that's less fun!  

```solidity
// pseudoish code
unchecked {
  uint256 p = priceRange * currentStep;
  if (p / a != b) p = uint256
}
```
