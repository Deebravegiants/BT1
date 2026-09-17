# [M] [MEDIUM] MeritDutchAuction#getPriceAt - priceRange * currentStep could cause an overflow rendering the MeritDutchAuction contract unusable

## Summary
Severity: Medium
Reporter: vangrim
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122
Type: audit-issue

## Details
# [MEDIUM] MeritDutchAuction#getPriceAt - priceRange * currentStep could cause an overflow rendering the MeritDutchAuction contract unusable

## Summary
The `MeritDutchAuction#getPriceAt` function uses the multiplication operation`priceRange * currentStep`, which could potentially trigger an overflow. If this occurs, the mint function could be unusable, rendering the MeritDutchAuction contract unusable.

## Vulnerability Detail
The `getPriceAt` function, which calculates the current price by multiplying `priceRange` and `currentStep` on line 122, could result in an overflow if the `priceRange` or `currentStep` values are exceedingly large.

## Impact
The potential overflow in the `getPriceAt` function of the `MeritDutchAuction` contract could essentially render the mint function non-functional as the `getPriceAt` function is called by the mint function.

## Code Snippet
The code of concern within the MeritDutchAuction#getPriceAt function is as follows:
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L122

```solidity
uint256 price = startPrice - (priceRange * currentStep / totalSteps);
```

## Tool used

Manual Review

## Recommendation
To safeguard against this overflow vulnerability, you can introduce an overflow check in the `getPriceAt` function, as shown below:

```solidity
// Handle potential overflow in a safe way
if (priceRange > type(uint256).max / currentStep) {
    // If an overflow is likely or totalSteps is zero, return a safe value
    // Depending on your needs, you might return startPrice, endPrice, or some other value
    return startPrice;
}
```
