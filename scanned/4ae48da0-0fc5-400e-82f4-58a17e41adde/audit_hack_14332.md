# [H] Price can underflow due to bad settings and potentially brick the contract.

## Summary
Severity: High
Reporter: boredpukar
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L99
Type: audit-issue

## Details
# Price can underflow due to bad settings and potentially brick the contract.

## Summary

Improper configurations can potentially brick the contract.

## Vulnerability Detail

The auction contract is implemented by configuring a start price and price drop per second.

```solidity
uint256 timePassed = time - startTime;
uint256 totalSteps = (endTime - startTime) / stepSize;
uint256 currentStep = timePassed / stepSize;
uint256 priceRange = startPrice - endPrice;

// Calculate the price at the current step
uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```

A bad set of settings can cause an issue where the `priceRange * currentStep / totalStep` gets bigger than the start price and underflows the current price calculation.

This means that if `priceRange * currentStep / totalStep` > `startPrice`, then the unsigned integer result will become negative and underflow, leading to potentially bricking the contract and an eventual loss of funds.

## Impact

Due to Solidity 0.8 default checked math, the subtraction of the start price and the drop will cause a negative value that will generate an underflow in the unsigned integer type and lead to a transaction revert.

Calls to `getPrice` will revert, and since this function is used in the buy to calculate the current NFT price it will also cause the buy process to fail. The price drop will continue to increase as time passes, making it impossible to recover from this situation and effectively bricking the contract.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L99
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L106

```solidity
/// @notice Returns the current price
    function getPrice() public view returns(uint256) {
        // Use the current timestamp to get the current price
        return getPriceAt(block.timestamp);
    }

    /// @notice Returns the price at a given time
    /// @param time Timestampfunction getPriceAt(uint256 time) public view returns(uint256) {
        // If auction hasn't started yet, return start price
        if(time < startTime) {
            return startPrice;
        }
        // If auction has ended, return end price
        if(time >= endTime) {
            return endPrice;
        }

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

Add a validation in the contract to ensure that the current configuration can't underflow the price. 

```solidity
     // don't go negative in the next step
        if ((priceRange * currentStep / totalSteps) > startPrice) {
            // do something
        }
```
Use SafeMath library by OZ to ensure that the contract implementation automatically revert on possible underflow/overflow.
