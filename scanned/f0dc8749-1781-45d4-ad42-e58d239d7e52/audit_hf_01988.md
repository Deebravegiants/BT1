# [H] Uneven getPendingAccFundingFees() leading to wrong funding rate update

## Summary
Severity: High
Contest weight: 0.5574
Dataset id: 11150
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Ostium uses a velocity funding rate update, so the actual change is the integral of the velocity of the past time. There is a case when this update (which can be viewed as the area of the function, as shown in the docs) is done incorrectly. Namely, when absLastFundingRate is bigger than absNewFundingRate, the square part of the area (in the negative y axis), has side absNewFundingRate, but the docs and code use absLastFundingRate. Here is a poc. It can be seen that going from -5000 to 1000 gives a different change than -1000 to 5000.

## Recommendation
Update the docs and tweak the code to accommodate for this change, such as:
```solidity
function getPendingAccFundingFees(uint16 pairIndex)
public
view
returns (int256 valueLong, int256 valueShort, int64 fr)
{
...
if (absNewFundingRate > f.maxFundingFeePerBlock) {
...
} else {
...
uint256 squareHeight = absNewFundingRate < absLastFundingRate ?
absNewFundingRate : absLastFundingRate;
accumulated_funding_rate_change = int256(
(squareHeight + (uint256(numBlocksToCharge).ceilDiv(2) *
absLastVelocity))
* uint256(numBlocksToCharge)
);
...
}
}
```
