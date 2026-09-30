# [H] H-01 | Sweep DoS

## Summary
Severity: High
Contest weight: 0.1564
Dataset id: 22243
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In function drop, the liquidity added to the discovery range is liqMulWad(threshold, 1e18 + getLiquiditySpread()) while the liquidity added to the anchor range is liquidityA. The threshold can be smaller than the anchor’s liquidity, ultimately allowing the discovery’s liquidity to be thinner than the anchor’s liquidity. Because the invariant discovery liquidity ≥ anchor liquidity has been broken, function sweep can be DoS’d due to underflow when performing oldDiscovery.liquidity - liquidityA, preventing a core market making functionality from being usable.

## Recommendation
Minimize liquidityA between the threshold and the old anchor liquidity, as done in sweep and slide.
