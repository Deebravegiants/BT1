# [H] V3AMO integration with V3 does not collect LP fees when burning liq- uidity.

## Summary
Severity: High
Reporter: pkqs90
Contest weight: 0.7869
Dataset id: 2627
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
V3AMO supplies liquidity for the Boost-USD pool. When users call unfarmBuyBurn to burn liquidity from V3AMO, the LP fees should be collected as well. However, the current integration does not correctly collect fees for V3, and the fees are stuck forever. Let's see the V3 implementation for burnAndCollect() function. https://ftmscan.com/address/0x54a571D91A5F8beD1D56fC09756F1714F0cd8aD9#code (This is taken from notion docs.) Even though V3 is a fork of UniswapV3, there is a significant difference. In UniswapV3, the liquidity fees are calculated within the Pool, and can be collected via the Pool. However, in V3, the fees are not updated at all (In the following code, where the fees should be updated in Position.sol as done by UniswapV3, you can see the fee update code is fully removed). Also, according to the V3 docs https://docs..com/v3/rewards-distributor, all fees (and bribes) distribution have been moved into the RewardsDistributor.sol contract, and distributed via merkel proof. This means calling burnAndCollect() does not allow us to collect the LP fees anymore, and that we need to call separate function for V3AMO in order to retrieve the LP fees.
```solidity
function burnAndCollect(
    address recipient,
    int24 tickLower,
    int24 tickUpper,
    uint128 amountToBurn,
    uint128 amount0ToCollect,
    uint128 amount1ToCollect
)
external
override
returns (uint256 amount0FromBurn, uint256 amount1FromBurn, uint128 amount0Collected, uint128 amount1Collected)
{
    (amount0FromBurn, amount1FromBurn) = _burn(tickLower, tickUpper, amountToBurn);
    (amount0Collected, amount1Collected) = _collect(
        recipient,
        tickLower,
        tickUpper,
        amount0ToCollect,
        amount1ToCollect
    );
}

function _burn(
    int24 tickLower,
    int24 tickUpper,
    uint128 amount
) private lock returns (uint256 amount0, uint256 amount1) {
    (Position.Info storage position, int256 amount0Int, int256 amount1Int) = _modifyPosition(
        ModifyPositionParams({
            owner: msg.sender,
            tickLower: tickLower,
            tickUpper: tickUpper,
            liquidityDelta: -int256(amount).toInt128()
        })
    );
    amount0 = uint256(-amount0Int);
    amount1 = uint256(-amount1Int);
    if (amount0 > 0 || amount1 > 0) {
        (position.tokensOwed0, position.tokensOwed1) = (
            position.tokensOwed0 + uint128(amount0),
            position.tokensOwed1 + uint128(amount1)
        );
    }
    emit Burn(msg.sender, tickLower, tickUpper, amount, amount0, amount1);
}

function _modifyPosition(
    ModifyPositionParams memory params
) private returns (Position.Info storage position, int256 amount0, int256 amount1) {
    position = _updatePosition(params.owner, params.tickLower, params.tickUpper, params.liquidityDelta);
}

function _updatePosition(
    address owner,
    int24 tickLower,
    int24 tickUpper,
    int128 liquidityDelta
) private returns (Position.Info storage position) {
    position.update(liquidityDelta);
}

/// @notice Updates the liquidity amount associated with a user's position
/// @param self The individual position to update
/// @param liquidityDelta The change in pool liquidity as a result of the position update
function update(Info storage self, int128 liquidityDelta) internal {
    if (liquidityDelta != 0) {
        self.liquidity = LiquidityMath.addDelta(self.liquidity, liquidityDelta);
    }
}
```
V3AMO implementation
```solidity
function _unfarmBuyBurn(
    uint256 liquidity,
    uint256 minBoostRemove,
    uint256 minUsdRemove,
    uint256 minBoostAmountOut,
    uint256 deadline
)
internal
override
returns (uint256 boostRemoved, uint256 usdRemoved, uint256 usdAmountIn, uint256 boostAmountOut)
{
    (uint256 amount0Min, uint256 amount1Min) = sortAmounts(minBoostRemove, minUsdRemove);
    // Remove liquidity and store the amounts of USD and BOOST tokens received
    (
        uint256 amount0FromBurn,
        uint256 amount1FromBurn,
        uint128 amount0Collected,
        uint128 amount1Collected
    ) = IV3Pool(pool).burnAndCollect(
        address(this),
        tickLower,
        tickUpper,
        uint128(liquidity),
        amount0Min,
        amount1Min,
        type(uint128).max,
        type(uint128).max,
        deadline
    );
}
```
Internal pre-conditions N/A External pre-conditions N/A Attack Path N/A LP Fees are not retrievable for V3AMO.

## Recommendation
Add a function to call the RewardsDistributor.sol for V3 to retrieve the LP fees. This can be an independent function, since not all V3 forks may support this feature.
