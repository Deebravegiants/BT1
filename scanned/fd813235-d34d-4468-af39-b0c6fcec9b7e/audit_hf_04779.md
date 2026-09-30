# [M] balanceOf function is not updated with the re-

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 22628
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The balanceOf function calculates the interest that has been paid to the aToken holders using indexes. However, it does not simulate the rebasing token yield.
As we can see in the balanceOf function, the reserved normal income is used to derive the actual value of the tokens:
```solidity
function balanceOf(
    address user
) public view override(IncentivizedERC20, IERC20) returns (uint256) {
    return super.balanceOf(user).rayMul(_pool.getReserveNormalizedIncome(_underlyingAsset));
}
```
Typically, the index adds the rebasing token yield, as observed here:
```solidity
function _updateIndexes(
    DataTypes.ReserveData storage reserve,
    uint256 scaledVariableDebt,
    uint256 liquidityIndex,
    uint256 variableBorrowIndex,
    uint40 timestamp
) internal returns (uint256, uint256) {
    uint256 currentLiquidityRate = reserve.currentLiquidityRate;
    uint256 newLiquidityIndex = liquidityIndex;
    uint256 newVariableBorrowIndex = variableBorrowIndex;
    //only cumulating if there is any income being produced
    if (currentLiquidityRate > 0) {
        uint256 cumulatedLiquidityInterest = MathUtils.calculateLinearInterest(
            currentLiquidityRate,
            timestamp
        );
        newLiquidityIndex = cumulatedLiquidityInterest.rayMul(liquidityIndex);
        require(newLiquidityIndex <= type(uint128).max,
            Errors.RL_LIQUIDITY_INDEX_OVERFLOW);
        reserve.liquidityIndex = uint128(newLiquidityIndex);
        //as the liquidity rate might come only from stable rate loans, we need to ensure
        //that there is actual variable debt before accumulating
        if (scaledVariableDebt != 0) {
            uint256 cumulatedVariableBorrowInterest =
                MathUtils.calculateCompoundedInterest(
                    reserve.currentVariableBorrowRate,
                    timestamp
                );
            newVariableBorrowIndex =
                cumulatedVariableBorrowInterest.rayMul(variableBorrowIndex);
            require(
                newVariableBorrowIndex <= type(uint128).max,
                Errors.RL_VARIABLE_BORROW_INDEX_OVERFLOW
            );
            reserve.variableBorrowIndex = uint128(newVariableBorrowIndex);
        }
    }
    // check for blast native yield if underlying asset is USDB or WETHRebasing
    // if pending, claim yield and accrue it as interest to aToken holders
    address aTokenAddress = reserve.aTokenAddress;
    address underlyingAsset = IAToken(aTokenAddress).UNDERLYING_ASSET_ADDRESS();
    // claimableAmount always has 18 decimals, since both USDB and WETH have 18 decimals
    uint256 claimableAmount = (underlyingAsset == USDB || underlyingAsset == WETH)
        ? IERC20Rebasing(underlyingAsset).getClaimableAmount(address(this))
        : 0;
    // only accrue native yield if there is something to be claimed
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
}
```
However, when calculating the view function for reserve normalized income, it does not add the rebasing yield:
```solidity
function getNormalizedIncome(
    DataTypes.ReserveData storage reserve
) internal view returns (uint256) {
    uint40 timestamp = reserve.lastUpdateTimestamp;
    //solium-disable-next-line
    if (timestamp == uint40(block.timestamp)) {
        //if the index was updated in the same block, no need to perform any calculation
        return reserve.liquidityIndex;
    }
    uint256 cumulated = MathUtils
        .calculateLinearInterest(reserve.currentLiquidityRate, timestamp)
        .rayMul(reserve.liquidityIndex);
    return cumulated;
}
```
If balanceOf returns different numbers, lot's of functionality will not work such as repaying the entire balance of a user, depositing and withdrawing since the balanceOf used inside these functions and expected to be same as the actual balance that the user holds. For example:
otocol-v2/contracts/protocol/lendingpool/LendingPool.sol#L151-L157
otocol-v2/contracts/protocol/lendingpool/LendingPool.sol#L285

## Recommendation
No recommendation available
