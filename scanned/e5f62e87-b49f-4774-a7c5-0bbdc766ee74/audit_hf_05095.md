# [H] Exercising a large amount of options gives significantly better price due to flawed TWAP

## Summary
Severity: High
Contest weight: 0.5955
Dataset id: 23119
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Exercising options in multiple transactions would be significantly more profitable. Within the OptionTokenV4 contract, in order to calculate the paymentAmount the contract uses its own interpretation of TWAP price. But instead of it just being the actual TWAP price, it's the average amountOut a user would receive during 4 consecutive periods of time.
```solidity
function getTimeWeightedAveragePrice(
    uint256 _amount
) public view returns (uint256) {
    uint256[] memory amtsOut = IPair(pair).prices(
        underlyingToken,
        _amount,
        twapPoints
    );
    uint256 len = amtsOut.length;
    uint256 summedAmount;
    for (uint256 i = 0; i < len; i++) {
        summedAmount += amtsOut[i];
    }
    return summedAmount / twapPoints;
}
```
This would mean that the more option tokens are exercised, the better the price would be. (Since the more you swap into the AMM, the more valuable the output token becomes).
A simple example would be if there has been 1e18 of reserves in both tokens.
1. Exercising an option for 0.1e18 would cost you 0.09e18 payment token. Average payment/underlying price = 0.9
2. Exercising an option for 100e18 would cost you 0.99e18 payment token. Average payment/underlying price = 0.01
User will be able to exercise options at significantly higher discount than supposed to.

## Recommendation
Do not use amountsOut as a way to price the options.
