# [H] Underlying LP value can be manipulated to drain

## Summary
Severity: High
Contest weight: 0.7857
Dataset id: 22607
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Both the orange and teahouse utilizes slot0 to determine the value of the vault when depositing or withdrawing. This allows manipulation of the pool value to withdraw more expected.
```solidity
// OrangeDopexV2LPAutomator.sol#L241-L272
function totalAssets() public view returns (uint256) {
    ...
    (uint160 _sqrtRatioX96, , , , , , ) = pool.slot0();
    for (uint256 i = 0; i < _length; ) {
        _lt = int24(uint24(activeTicks.at(i)));
        _ut = _lt + poolTickSpacing;
        _tid = handler.tokenId(address(pool), handlerHook, _lt, _ut);
        _liquidity = handler.convertToAssets((handler.balanceOf(address(this), _tid)).toUint128(), _tid);
        (_a0, _a1) = LiquidityAmounts.getAmountsForLiquidity(
            _sqrtRatioX96,
            _lt.getSqrtRatioAtTick(),
            _ut.getSqrtRatioAtTick(),
            _liquidity
        );
        _sum0 += _a0;
        _sum1 += _a1;
        unchecked {
            i++;
        }
    }
```
First to show that the value of liquidity is determined using slot0 which is easily manipulated. Above is shown the Orange vault which slot0 to determine the price to calculate underlying assets.
```solidity
// TeaVaultV3Pair.sol#L673-L676
function estimatedValueInToken0() external override view returns (uint256 value0) {
    (uint256 _amount0, uint256 _amount1) = vaultAllUnderlyingAssets();
    value0 = VaultUtils.estimatedValueInToken0(pool, _amount0, _amount1);
}
// VaultUtils.sol#L131-L143
function estimatedValueInToken0(
    IUniswapV3Pool pool,
    uint256 _amount0,
    uint256 _amount1
) external view returns (uint256 value0) {
    (uint160 sqrtPriceX96, , , , , , ) = pool.slot0();
    value0 = _amount0 + FullMath.mulDiv(
        _amount1,
        sqrtPriceX96,
        FixedPoint96.Q96
    );
}
```
We see the same thing for teahouse, using slot0 to calculate the price of the second asset. Next is to show how value can be manipulated. Assume we have a pool of 2 assets each worth $1 containing 100 of each asset. At rest our pool is worth: $1 * 100 + $1 * 100 = $200. Now swap 100 asset0 to manipulate the price. This leaves the pool with 200 token0 and 50 token1. Recalculate our value: $1 * 200 + 50 * $1. The pool is now valued at $250. This alone is not enough to exploit the pool. You see if you were to withdraw at this manipulated value then the attacker would lose the same amount of value that they would gain since they must restore the pool to it's previous price. withdraw from a pool that is not manipulated. Assume we utilize two of the pools like the one described and there is 400 LP. The total value of the pools are $400 and each LP should be worth $1. Now we manipulate one pool and it is worth $250. This brings the total value to $450 and the contract thinks each LP is worth $450/400 = $1.125. Now we can withdraw from the other pool that is not manipulated. Since that pool is not manipulated the attack will be profitable. The attack would flow as shown:
1. Assume there are two underlying pools
2. Manipulate the price of one pool to increase LP price
3. Withdraw from the other vault that isn't manipulated
4. Restore the first pool to the market price
5. Profit
Orange and teahouse warehouses can drained by manipulating underlying pools

## Recommendation
Use chainlink oracles to calculate share value instead of using the underlying vaults.
