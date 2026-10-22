# [H] IV Can be Decreased for Free

## Summary
Severity: High
Contest weight: 0.6325
Dataset id: 20364
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquidity at a single tickSpacing is used to calculate the IV. The more liquidity is in this tick spacing, the lower the IV, as demonstrated by the tickTvl dividing the return value of the estimate function:
```solidity
return SoladyMath.sqrt((4e24 * volumeGamma0Gamma1 * scale) / (b.timestamp - a.timestamp) / tickTvl);
```
Since this is using data only from the block that the function is called, the liquidity can easily be increased by: 1. depositing a large amount liquidity into the tickSpacing 2. calling update 3. removing the liquidity active liquidity tick. Therefore, the capital cost required to massively increase the liquidity is low. Additionally, the manipulation has zero cost (aside from gas fees), as no trading is done through the pool. Contrast this with a pool price manipulation, which costs a significant amount of trading fees to trade through a large amount of the liquidity of the pool. Since this manipulation costs nothing except gas, the IV_CHANGE_PER_UPDATE which limits the amount that IV can be manipulated per update does not sufficiently disincentivise manipulation, it just extends the time period required to manipulate. Decreasing the IV increases the LTV, and due to the free cost, it's reasonable to increase the LTV to the max LTV of 90% even for very volatile assets. Aloe uses the IV to estimate the probability of insolvency of loans. With the delay inherent in TWAP oracle and the liquidation delay by the warn-then-liquidate process, this manipulation can turn price change based insolvency from a 5 sigma event (as designed by the protocol) to a likely event.
• Decreasing IV can be done at zero cost aside from gas fees.
• This can be used to borrow assets at far more leverage than the proper LTV
• Borrowers can use this to avoid liquidation
• This also breaks the insolvency estimation based on IV for riskiness of price-change caused insolvency.

## Recommendation
Use the time weighted average liquidity of in-range ticks of the recent past, so that single block + single tickSpacing liquidity deposits cannot manipulate IV significantly.
