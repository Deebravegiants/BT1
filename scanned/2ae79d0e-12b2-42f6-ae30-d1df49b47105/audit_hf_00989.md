# [M] Insufficient Observations for TWAP Calculation

## Summary
Severity: Medium
Contest weight: 0.5925
Dataset id: 3131
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Ascendant.sol, when the Uniswap V3 pool is created, the observation cardinality is set to 100:
```solidity
function _createUniswapV3Pool(
    IQuoter quoter = IQuoter(UNISWAP_V3_QUOTER);
    uint256 dragonXAmount = quoter.quoteExactInput(path, INITIAL_TITAN_X_FOR_LIQ);
    uint256 ascendantAmount = INITIAL_ASCENDANT_FOR_LP;
    (address token0, address token1) = _ascendant < _dragonX ? (_ascendant, _dragonX) : (_dragonX, _ascendant);
    (uint256 amount0, uint256 amount1) = token0 == _dragonX ? (dragonXAmount, ascendantAmount) : (ascendantAmount, dragonXAmount);
    uint160 sqrtPX96 = uint160((sqrt((amount1 * 1e18) / amount0) * 2 ** 96) / 1e9);
    INonfungiblePositionManager manager = INonfungiblePositionManager(UNISWAP_V3_POSITION_MANAGER);
    _pool = manager.createAndInitializePoolIfNecessary(token0, token1, POOL_FEE, sqrtPX96);
    IUniswapV3Pool(_pool).increaseObservationCardinalityNext(uint16(100));
```
Observations are snapshots of the state of the pool, specifically time-weighted average values such as prices and liquidity. These observations are used to calculate the TWAP. 100 observations provide good coverage for TWAP calculations, but maybe not enough if the pool is quite active or the lookback period is larger (20-30 minutes). We can see that the Time-Weighted Average Price (TWAP) lookback period will be between 5 and 30 minutes:
```solidity
function setSlippageConfig(
    IUniswapV3Pool pool,
    uint128 _newSlippage,
    uint32 _newLookBack
) external notAmount0(_newLookBack) onlySlippageAdminOrOwner {
    require(_newLookBack >= 5 && _newLookBack <= 30, "SwapActions__InvalidLookBack()");
    require(_newSlippage <= WAD, "SwapActions__InvalidSlippage()");
    emit SlippageConfigChanged(pool, _newSlippage, _newLookBack);
    slippageConfigs[pool] = Slippage({slippage: _newSlippage, twapLookback: _newLookBack});
}
```
Suppose the TWAP lookback period is increased to a maximum of 30 minutes. In that case, the 100 observations may not be enough to provide accurate price data for highly active pools, as they might only cover the most recent 10-20 minutes.

## Recommendation
Increasing the observation cardinality to 150-200.
