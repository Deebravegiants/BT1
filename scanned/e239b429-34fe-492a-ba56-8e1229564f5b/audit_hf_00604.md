# [M] M-02 | updateTicks Should Use Previous Liquidity

## Summary
Severity: Medium
Contest weight: 0.1818
Dataset id: 2103
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _updateTicks function of the MarketMaking policy there is logic to alter the upper tick of the
anchor position based upon the liquidity of the Discovery position relative to the Anchor position
liquidity.
This is done to ideally prevent bAsset supply being minted in excess of the Discovery position
liquidity in the range above the price in the Anchor position.
This reduces the magnitude of an arbitrage opportunity that would arise from selling through the
Discovery range into the Anchor range and beneﬁtting from the increased liquidity due to a higher
leverage of the Anchor.
However in such an arbitrage scenario, the liquidity that the Anchor position should be compared
against is the liquidity of the previous Discovery position rather than the liquidity of the current
Discovery position.
This is because the old Discovery position is the one which is sold through to reach the new Anchor
range and thus trigger the rebalance and therefore is the liquidity which the Arbitrage economics are
based upon.
As a result the Anchor range upper tick handling should consider the liquidity of the old Discovery
position rather than the current result of the _getThresholdLiquidity function, which will be the new
Discovery position liquidity.

## Recommendation
Consider comparing the predicted anchor liquidity against the minimum of both the result of the
_getThresholdLiquidity and the old Discovery position liquidity to be the most conservative in limiting
the arbitrage opportunities from selling through the Discovery position.
