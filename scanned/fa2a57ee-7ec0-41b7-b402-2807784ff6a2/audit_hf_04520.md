# [M] M-01 | Mismatching Max Tick Boundary

## Summary
Severity: Medium
Contest weight: 0.1546
Dataset id: 22084
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The baseAssetMaxPriceTick is the input parameter to createValid to set the maximum trading tick of the epoch. However, this tick is not the same tick that is used in epoch.sqrtPriceMaxX96 or epoch.maxPriceD18 as the Uniswap tickSpacing is added to the tick. It is important to distinguish between ticks and tickSpacing. Each tick is 0.01% price difference apart. A tickSpacing contains multiple ticks depending on the fee tier, and for a 1% fee pool this is 200 ticks which corresponds to a 2.02% price difference. Therefore, epoch.maxPriceD18 and baseAssetMaxPriceTick correspond to different ticks which are 2.02% price difference apart. The maxPriceD18 is used to bound the settlement price, and is also the highestPrice during trades. baseAssetMaxPriceTick is used in the validateLp function, which limits the range which liquidity is added. Since the baseAssetMaxPriceTick is lower than maxPriceD18, it is impossible for liquidity to be added up to the maximum price, and consequently for traders to swap to that price.

## Recommendation
Consider consistently using the baseAssetMaxPriceTick to derive the max tick and max price without adding a tick spacing. If tick adjustment is necessary, consider adding a single tick rather than an entire tickSpacing.
