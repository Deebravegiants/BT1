# [M] Incorrect calculation of TWAP in OptionTo-

## Summary
Severity: Medium
Contest weight: 0.4074
Dataset id: 23110
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The average price returned by OptionTokenV4.getTimeWeightedAveragePrice() can be up to 30 minutes outdated and does not reflect the current Token price. In the getTimeWeightedAveragePrice() function, the average price is calculated using the last X known price observations from the Pair contract. However, this approach has a flaw because it does not consider the current price, which could be as much as 30 minutes old. Consider a scenario where the price of the Token significantly increases during this 30-minute window. The resulting maximum discount might not adequately cover the percentage increase in price. This could lead to the protocol failing to collect proper fees when exercising the Tokens. The use of an outdated TWAP price could result in losses for the protocol or users.

## Recommendation
To address this issue, incorporating also the current price retrieved from Pair.current() function:
```solidity
function getTimeWeightedAveragePrice(uint256 _amount) public view returns (uint256) {
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
    summedAmount += IPair(pair).current(underlyingToken, _amount);
    return (summedAmount / twapPoints) + 1;
}
```
