# [M] `_getUniswapTwapWei`

## Summary
Severity: Medium
Contest weight: 0.4672
Dataset id: 20705
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Take a look at <https://github.com/code-423n4/2024-01-salty/blob/f742b554e18ae1a07cb8d4617ec8aa50db037c1c/src/price_feed/CoreUniswapFeed.sol#L49-L75>

```solidity
// Returns amount of token0 * (10**18) given token1
function _getUniswapTwapWei( IUniswapV3Pool pool, uint256 twapInterval ) public view returns (uint256)
	{
		uint32[] memory secondsAgo = new uint32[](2);
		secondsAgo[0] = uint32(twapInterval); // from (before)
		secondsAgo[1] = 0; // to (now)

		// Get the historical tick data using the observe() function
		(int56[] memory tickCumulatives, ) = pool.observe(secondsAgo);
		// @audit
		int24 tick = int24((tickCumulatives[1] - tickCumulatives[0]) / int56(uint56(twapInterval)));
		uint160 sqrtPriceX96 = TickMath.getSqrtRatioAtTick( tick );
		uint256 p = FullMath.mulDiv(sqrtPriceX96, sqrtPriceX96, FixedPoint96.Q96 );

		uint8 decimals0 = ( ERC20( pool.token0() ) ).decimals();
		uint8 decimals1 = ( ERC20( pool.token1() ) ).decimals();

		if ( decimals1 > decimals0 )
			return FullMath.mulDiv( 10 ** ( 18 + decimals1 - decimals0 ), FixedPoint96.Q96, p );

		if ( decimals0 > decimals1 )
			return ( FixedPoint96.Q96 * ( 10 ** 18 ) ) / ( p * ( 10 ** ( decimals0 - decimals1 ) ) );

		return ( FixedPoint96.Q96 * ( 10 ** 18 ) ) / p;
	}
```

This function is used to get twap price tick using uniswap oracle. it uses `pool.observe()` to get `tickCumulatives` array which is then used to calculate `int24 tick`.

The problem is that in case if `int24(tickCumulatives[1] - tickCumulatives[0])` is negative, then the tick should be rounded down as it’s done in the[ uniswap library](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol#L36).

As result, in case if `int24(tickCumulatives[1] - tickCumulatives[0])` is negative and `(tickCumulatives[1] - tickCumulatives[0]) % secondsAgo != 0`, then returned tick will be bigger then it should be, which opens possibility for some price manipulations and arbitrage opportunities.

## Recommendation
Add this line: `if (tickCumulatives[1] - tickCumulatives[0] < 0 && (tickCumulatives[1] - tickCumulatives[0]) % secondsAgo != 0) timeWeightedTick --;`

Now rounds down for negative ticks as suggested.

<https://github.com/othernet-global/salty-io/commit/4625393e9bd010778003a1424201513885068800>

The stablecoin framework: /stablecoin, /price_feed, WBTC/WETH collateral, PriceAggregator, price feeds and USDS have been removed: <https://github.com/othernet-global/salty-io/commit/88b7fd1f3f5e037a155424a85275efd79f3e9bf9>
