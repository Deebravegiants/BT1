# [H] `_getReferencePoolPriceX96`

## Summary
Severity: High
Contest weight: 0.6375
Dataset id: 20966
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Take a look [here](https://github.com/code-423n4/2024-03-revert-lend/blob/457230945a49878eefdc1001796b10638c1e7584/src/V3Oracle.sol#L357-L374).
```solidity
function _getReferencePoolPriceX96(IUniswapV3Pool pool, uint32 twapSeconds) internal view returns (uint256) {
    uint160 sqrtPriceX96;
    // if twap seconds set to 0 just use pool price
    if (twapSeconds == 0) {
        (sqrtPriceX96,,,,,,) = pool.slot0();
    } else {
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = 0; // from (before)
        secondsAgos[1] = twapSeconds; // from (before)
        (int56[] memory tickCumulatives,) = pool.observe(secondsAgos); // pool observe may fail when there is not enough history available (only use pool with enough history!)
        //@audit
        int24 tick = int24((tickCumulatives[0] - tickCumulatives[1]) / int56(uint56(twapSeconds)));
        sqrtPriceX96 = TickMath.getSqrtRatioAtTick(tick);
    }

    return FullMath.mulDiv(sqrtPriceX96, sqrtPriceX96, Q96);
}
```
This function is used to calculate the reference pool price. It uses either the latest slot price or TWAP based on twapSeconds.

Now note that [unlike the original uniswap implementation](https://github.com/Uniswap/v3-periphery/blob/697c2474757ea89fec12a4e6db16a574fe259610/contracts/libraries/OracleLibrary.sol#L30), here the delta of the tick cumulative is being calculated in a different manner, i.e [protocol implements (`tickCumulatives`[0] - `tickCumulatives`[1]](https://github.com/code-423n4/2024-03-revert-lend/blob/457230945a49878eefdc1001796b10638c1e7584/src/V3Oracle.sol#L369) instead of `tickCumulatives[1] - (tickCumulatives[0]` which is because here, `secondsAgos[0] = 0;` and `secondsAgos[1] = twapSeconds;`; unlike [in Uniswap OracleLibrary](https://github.com/Uniswap/v3-periphery/blob/697c2474757ea89fec12a4e6db16a574fe259610/contracts/libraries/OracleLibrary.sol#L23C1-L26C1) where `secondsAgos[0] = secondsAgo;` and `secondsAgos[1] = 0;`, so everything checks out and the tick deltas are calculated accurately, i.e in our case `tickCumulativesDelta = tickCumulatives[0] - tickCumulatives[1]`.

The problem now is that in the case if our `tickCumulativesDelta` is negative, i.e `int24(tickCumulatives[0] - tickCumulatives[1] < 0)` , then the tick should be rounded down, as it’s done in the[ uniswap library](https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol#L36).

But this is not being done and as a result, in the case if `int24(tickCumulatives[0] - tickCumulatives[1])` is negative and `(tickCumulatives[0] - tickCumulatives[1]) % secondsAgo != 0`, then the returned tick will be bigger then it should be; which opens possibility for some price manipulations and arbitrage opportunities.

## Recommendation
Add this line: `if (tickCumulatives[0] - tickCumulatives[1] < 0 && (tickCumulatives[0] - tickCumulatives[1]) % secondsAgo != 0) timeWeightedTick --;`.
