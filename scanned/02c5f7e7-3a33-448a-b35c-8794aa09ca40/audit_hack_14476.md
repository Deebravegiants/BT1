# [M] Users will be paying `startPrice` during auction period when `stepSize` equals to the auction duration

## Summary
Severity: Medium
Reporter: hals
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L76-L78
Type: audit-issue

## Details
# Users will be paying `startPrice` during auction period when `stepSize` equals to the auction duration

## Summary

Users will be paying `startPrice` during auction period when `stepSize` equals to the auction duration

## Vulnerability Detail

- The idea of `MeritDutchAuction` is to get users competing to mint the project limited NFTs; while the price starts high at `startPrice` and decrements with each time step during the auction period until it reachs `endPrice` (lowest price) at the end.
- In `MeritDutchAuction` contract :
  the `stepSize` which is used to calculate the decrement of `startPrice` with time is checked against two conditions:

first check:

```solidity
require(stepSize_ > 0, "Step size must be greater than 0");
```

second check:

```solidity
 require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");
```

- But it's not checked if the `stepSize` equals to `endTime_ - startTime_` (auction duration); if it equals to this value; then users will be paying the highest price (`startPrice`) during the auction, which distrubts the idea of dutch auctions.

- The price is calculated by `getPriceAt` function: which first calculates the current step then the price based on the current step and the price range:

```solidity
  function getPriceAt(uint256 time) public view returns(uint256) {
     //...
        uint256 timePassed = time - startTime;
        uint256 totalSteps = (endTime - startTime) / stepSize; //@audit : will equal 1 when stepSize == endTime - startTime
        uint256 currentStep = timePassed / stepSize; //@audit : as long as time < endTime; currentStep will be zero
        uint256 priceRange = startPrice - endPrice;

        // Calculate the price at the current step
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);//@audit : will be startPrice
        return price;
    }
```

## Impact

Users will be tricked during the auction period to pay with the highest price.

## Code Snippet

- In `MeritDutchAuction.sol`/ `constructor` : [L76-L78](https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L76-L78)

```solidity
        require(stepSize_ > 0, "Step size must be greater than 0");
        // Duration must be a multiple of step size
        require((endTime_ - startTime_) % stepSize_ == 0, "Step size must be multiple of total duration");
```

- In `MeritDutchAuction.sol`/ `getPriceAt` function : [L116-L123](https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L116-L123)

```solidity
  function getPriceAt(uint256 time) public view returns(uint256) {
     //...
        uint256 timePassed = time - startTime;
        uint256 totalSteps = (endTime - startTime) / stepSize;
        uint256 currentStep = timePassed / stepSize;
        uint256 priceRange = startPrice - endPrice;

        // Calculate the price at the current step
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);
        return price;
    }
```

## Tool used

Manual Review

## Recommendation

Add this check in the constructor before assigning `stepSize`:

```solidity
  require(stepSize_  != endTime_ - startTime_);
```
