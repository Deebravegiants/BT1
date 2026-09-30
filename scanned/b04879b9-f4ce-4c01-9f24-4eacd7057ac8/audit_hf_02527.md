# [M] SwapAction.getTwapAmountV3(): the implemented fallback mechanism for secondsAgo is vulnerable to price manipulation

## Summary
Severity: Medium
Contest weight: 0.5943
Dataset id: 13517
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`SwapAction.getTwapAmountV3()` function is called whenever a swap action is invoked via `swapExactInputV3()`, where it uses twap to ensure the swap is performed within the slippage tolerance:
```solidity
function getTwapAmountV3(address tokenIn, address tokenOut, uint256 amount)
    public
    view
    returns (uint256 twapAmount, uint224 slippage)
{
    PoolAddress.getPoolKey(tokenIn, tokenOut, POOL_FEE));
    Slippage memory slippageConfig = slippageConfigs[poolAddress];
    if (slippageConfig.twapLookback == 0 && slippageConfig.slippage == 0) {
        slippageConfig = Slippage({twapLookback: 15, slippage: WAD - 0.2e18});
    }
    uint32 secondsAgo = slippageConfig.twapLookback * 60;
    uint32 oldestObservation = OracleLibrary.getOldestObservationSecondsAgo(poolAddress);
    if (oldestObservation < secondsAgo) secondsAgo = oldestObservation;
    (int24 arithmeticMeanTick,) = OracleLibrary.consult(poolAddress, secondsAgo);
    uint160 sqrtPriceX96 = TickMath.getSqrtRatioAtTick(arithmeticMeanTick);
    slippage = slippageConfig.slippage;
    twapAmount = OracleLibrary.getQuoteForSqrtRatioX96(sqrtPriceX96, amount, tokenIn, tokenOut);
}
```
where the `oldestObservation` represents the timestamp difference between the oldest recorded observation and the current time.

If `secondsAgo` (the TWAP window) exceeds `oldestObservation`, the function defaults `secondsAgo` to `oldestObservation` as a fallback mechanism instead of reverting:
```solidity
if (oldestObservation < secondsAgo) secondsAgo = oldestObservation;
```
But `oldestObservation < secondsAgo` means that the pool doesn't have enough historical data (low cardinality), and the available data will be used regardless of its correctness.

In UNI-V3, the oldest observation can be updated when the first trade occurs in a new block, and if the pool has low cardinality (initialized to 1 for example) and the fallback mechanism uses `oldestObservation` as `secondsAgo`, then any malicious actor can frontrun the `swapExactInputV3()` with a malicious trade before the TWAP is calculated to manipulate the price (inflate it) which will result in returning low calculated twapAmount that wouldn't protect against slippage.

## Recommendation
revert the txn if `oldestObservation < secondsAgo`. ensure that the used pools have a sufficient number of cardinality. use Chainlink oracles as a fallback in case twap fails.
