# [H] Index logic is flawed

## Summary
Severity: High
Contest weight: 0.7844
Dataset id: 22625
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When indexes are updated, on top of the interest rate updates the rebasing rewards will also be added. However, the handling of it is wrong.
AAVE V2 liquidityIndex is calculated as: newLiquidityIndex = previousLiquidityIndex * (total interest accrued since last time + 1) in RAY units.
This is how the (total interest accrued since last time) is calculated:
```solidity
function calculateLinearInterest(uint256 rate, uint40 lastUpdateTimestamp)
    internal
    view
    returns (uint256)
{
    //solium-disable-next-line
    uint256 timeDifference = block.timestamp.sub(uint256(lastUpdateTimestamp));
    return (rate.mul(timeDifference) / SECONDS_PER_YEAR).add(WadRayMath.ray());
}
```
The crucial aspect here is the addition of 1e27 to the value. The return of the calculateLinearInterest function is guaranteed to be a number greater than 1e27.
Therefore, multiplying the previousIndex by the new value will also ensure that the result is in 1e27 decimals.
Regarding the addition lines that Seismic adds to include rebasing rewards in the index:
```solidity
if (claimableAmount > 0) {
    uint256 totalPoolHoldings =
        IERC20(underlyingAsset).balanceOf(aTokenAddress) + // pool liquidity
        IERC20(reserve.stableDebtTokenAddress).totalSupply() + // total stable debt
        IERC20(reserve.variableDebtTokenAddress).totalSupply(); // total variable debt
    // express claimable amount as a percentage of pool assets and convert from wad to ray
    uint256 claimedInterestIndex =
        claimableAmount.wadDiv(totalPoolHoldings).wadToRay();
    // update pool liquidity index to reflect accrued native
    newLiquidityIndex = claimedInterestIndex.rayMul(newLiquidityIndex);
    reserve.liquidityIndex = uint128(newLiquidityIndex);
    require(newLiquidityIndex <= type(uint128).max,
        Errors.RL_LIQUIDITY_INDEX_OVERFLOW);
    // claim and send yield to the aToken
    IERC20Rebasing(underlyingAsset).claim(address(aTokenAddress),
        claimableAmount);
}
//solium-disable-next-line
reserve.lastUpdateTimestamp = uint40(block.timestamp);
```
now, let's assume the claimable rewards are 1e18 and there are 100e18 tokens in total at aToken/vTokens. claimableAmount = 1e18 totalPoolHoldings = 100e18 claimedInterestIndex = (1e18 * 1e18 / 100 * 1e18) * 1e9 = 10000000000000000000000000 = 0.01 * 1e27 the claimedInterestIndex is a value way lesser than 1e27 ! newLiquidityIndex = 0.01 * 1e27 * 1e27 / 1e27 = 0.01 * 1e27 new index is a value way lesser than 1e27!
The default value for both the liquidityIndex and variableBorrowIndex is 1e27 and should NEVER go below 1e27. However, as observed in the above example, it is very likely to occur. Even worse, when the claimable amount is too small, the claimedInterestIndex can be "0", resulting in the new liquidity index being "0", which would cause chaos for all users and prevent them from withdrawing, depositing, or borrowing.

## Recommendation
No recommendation available
