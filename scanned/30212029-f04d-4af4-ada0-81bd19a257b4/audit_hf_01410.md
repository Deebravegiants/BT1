# [M] calculateSpotPrice(...) should not use _normalizedTimeRemaining

## Summary
Severity: Medium
Contest weight: 0.4376
Dataset id: 7233
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When one trades on the curve, the following share-bond curve is used (with fixed ts):
c (z)^(1-ts) + y^(1-ts) = k
If one calculates the spot price which is the slope of the perpendicular line to the tangent of the curve at a point like (z, y) we would get:
dz / -dy = (1/c) * (z/y)^ts
Instead in calculateSpotPrice(...) the spot price is calculated as:
dz / -dy = (z/y)^(tr * ts)
There are two issues where the first is more important:
1. The (1/c) factor is not considered. This is due to a wrong NatSpec comment that mentions calculateSpotPrice(...) calculates the spot price without slippage of bonds in terms of shares, but it should be the spot price of bonds in terms of the base.
2. tr or _normalizedTimeRemaining does not have a concrete meaning since it is not used in the definition of the curve, but one can apply it to manipulate the price which will be used in fee calculations. But again those fee calculations should not consider the tr in the exponent when calculating fees for non-matured positions.
The spot price is recorded for oracles and is also used in LP and governance fee calculations.

## Recommendation
Based on the discussion with the client here calculateSpotPrice(...) should calculate (note the exponent term does not include tr):
dx / -dy = (dx/dz) * (dz/-dy) ≈ c * (dz/-dy) = (z/y)^ts
Also as a user probably we would want to query the average of dx / -dy from the oracle before investing.
And so calculateSpotPrice(...) needs to be changed to:
```solidity
/// @dev Calculates the spot price without slippage of bonds in terms of base.
/// @param _shareReserves The pool's share reserves.
/// @param _bondReserves The pool's bond reserves.
/// @param _initialSharePrice The initial share price as an 18 fixed-point value.
/// @param _timeStretch The time stretch parameter as an 18 fixed-point value.
/// @return spotPrice The spot price of bonds in terms of base as an 18 fixed-point value.
function calculateSpotPrice(
    uint256 _shareReserves,
    uint256 _bondReserves,
    uint256 _initialSharePrice,
    uint256 _timeStretch
) internal pure returns (uint256 spotPrice) {
    // (y / (mu * z)) ** -ts
    // ((mu * z) / y) ** ts
    spotPrice = _initialSharePrice
        .mulDivDown(_shareReserves, _bondReserves)
        .pow(_timeStretch);
}
```
