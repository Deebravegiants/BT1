# [M] Incorrect rounding in the

## Summary
Severity: Medium
Contest weight: 0.5805
Dataset id: 1956
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When buying and selling, the cost is calculated using rounding based on isPositive.
However, the rounding should be based on isBuy, not isPositive.
The _calcCost() function calculates cost by rounding based on isPositive.
If isPositive is false (indicating that DISTRUST votes are being traded), the calculation is rounded up.
Consider the following scenario:
1. A user buys 2 DISTRUST votes.
2. A user sells a DISTRUST vote.
3. A user sells another DISTRUST vote.
During the buying process, rounding up occurs once, but when selling, rounding up occurs twice—at steps 2 and 3. As a result, marketFunds will be decremented by a dust amount.
If marketFunds was originally 0 (with the market created by the admin at a 0 creation cost), then step 3 becomes impossible.
In fact, isPositive is never related to the rounding direction.
```solidity
function _calcCost(
    Market memory market,
    bool isPositive,
    bool isBuy,
    uint256 amount
) private pure returns (uint256 cost) {
    ...
    int256 costRatio = LMSR.getCost(
        market.votes[TRUST],
        market.votes[DISTRUST],
        voteDelta[0],
        voteDelta[1],
        market.liquidityParameter
    );
    uint256 positiveCostRatio = costRatio > 0 ? uint256(costRatio) : uint256(costRatio * -1);
    // multiply cost ratio by base price to get cost; divide by 1e18 to apply ratio
    cost = positiveCostRatio.mulDiv(
        market.basePrice,
        1e18,
        isPositive ? Math.Rounding.Floor : Math.Rounding.Ceil
    );
}
```
Internal pre-conditions
External pre-conditions
Attack Path
The last vote might not be sold.

## Recommendation
Use !isBuy instead of isPositive.
```solidity
cost = positiveCostRatio.mulDiv(
    market.basePrice,
    1e18,
    !isBuy ? Math.Rounding.Floor : Math.Rounding.Ceil
);
```
