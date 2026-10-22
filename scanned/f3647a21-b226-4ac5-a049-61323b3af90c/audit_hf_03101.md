# [M] hedgingTwapPeriod can exceed pool maximum

## Summary
Severity: Medium
Contest weight: 0.4133
Dataset id: 17499
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
hedgingTwapPeriod can exceed pool maximum twap period. On the Oracle contract’s getTwap function, _period means that number of seconds in the past to start calculating time-weighted average. In the CrabStrategyV2 contract, the period is set with hedgingTwapPeriod with _checkPeriod: true. However, if hedgingTwapPeriod exceeds the pool’s maximum twap period, that period is used, but hedgingTwapPeriod is ignored. Unexpected twap price calculation without hedgingTwapPeriod. CrabStrategyV2.solL786,Oracle.solL45 ```solidity function _isPriceHedge() internal view returns (bool) { uint256 wSqueethEthPrice = IOracle(oracle).getTwap(ethWSqueethPool, wPowerPerp, weth, hedgingTwapPeriod, true); uint256 cachedRatio = wSqueethEthPrice.wdiv(priceAtLastHedge); uint256 priceThreshold = cachedRatio > 1e18 ? (cachedRatio).sub(1e18) : uint256(1e18).sub(cachedRatio); return priceThreshold >= hedgePriceThreshold; } ```

## Recommendation
In the setHedgingTwapPeriod(), consider adding a check to ensure the pool’s maxi- mum twap period is at least hedgingTwapPeriod to let the set action take effect right after the transaction execution and avoid unexpected results as well. change the hedgingTwapPeriod after increasing the storage slots to have the storage slots fill up does not result in a different behavior vs increasing it right after an in- crease in storage slots for the uniswap oracle. We don’t anticipate this is something that will be changed frequently, if at all.
