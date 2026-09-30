# [M] M-03 | Anchor Liquidity Heavily Reduced

## Summary
Severity: Medium
Contest weight: 0.1737
Dataset id: 21483
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The slide operation scales down the ANCHOR liquidity using the inverseLiquidityPremium as follows: liquidityA = uint128(uint256(liquidityA).divWad((inverseLiquidityPremium))); The issue arises when all (or most) of the circulating supply is collateralized, and the leverage factor is a very large number. This means the liquidityA can drop to unexpected low values, creating high slippage to the users currently trading. If slide is triggered when the price is at the ANCHOR range (normal scenario), the operation will effectively remove most of the liquidity from the active trading range, moving the active reserves to the FLOOR range. Although he capacity of the system is still increasing, any subsequent sales will move the active tick into the FLOOR, something the protocol wants to avoid. In order to restore the correct liquidity of the ANCHOR, price will need to trade up into DISCOVERY and receive surplus reserves. Although this might temporarily restore the liquidity, the slide operation will keep scaling down the ANCHOR every time its triggered, as long as liquidityA > liquidityThreshold.

## Recommendation
Consider adding a max value to the leverage factor, limiting the reduction of the ANCHOR liquidity. Alternatively, consider using the following implementation for the getLeverageFactor function: leverageFactor_ = 1e18 + totalCollateral.mulWad(leverageRange).divWad(_bAssetsCirculating); Where leverageRange is a new variable configurable by the protocol. Otherwise consider implementing another implementation taking points 1 & 2 into account.
