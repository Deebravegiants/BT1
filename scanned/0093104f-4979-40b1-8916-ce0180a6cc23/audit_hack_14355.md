# [H] Users have to pay more price due to division round in calculation of price

## Summary
Severity: High
Reporter: mahdiRostami
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122
Type: audit-issue

## Details
# Users have to pay more price due to division round in calculation of price

## Summary
In mint() function in MeritDutchAuction, it uses “getPrice()” function for the calculation of the current price, but in “getPrice()” price is calculated in the following formula ```uint256 price = startPrice - (priceRange * currentStep / totalSteps);``` so It has division round issue.
## Vulnerability Detail
division round is common in solidity because solidity doesn't support floats.
## Impact
users have to pay more than acutal price
## Code Snippet
```solidity
        // Price being paid is the current price
        uint256 pricePaid = getPrice();
```
```solidity
    function getPrice() public view returns(uint256) {
        // Use the current timestamp to get the current price
        return getPriceAt(block.timestamp);
    }
```
```solidity
        uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```
[https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122)
## Tool used

Manual Review

## Recommendation
add a new varibale like ```uint256 constant EXP_PRECISION = 1e12;```
and change price calculation in following way:
```solidity 
uint256 price = startPrice * EXP_PRECISION - (priceRange * currentStep * EXP_PRECISION  / totalSteps);
price = price / EXP_PRECISION  ;
```
