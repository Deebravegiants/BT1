# [M] M-06 | Using LP For More Efficient Trades

## Summary
Severity: Medium
Contest weight: 0.1170
Dataset id: 1961
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Instead of opening a long position in the TradeModule to gain exposure vGas, traders can use the LiquidityModule for a more efficient strategy. By adding liquidity with a lower tick set to their desired entry price, traders can effectively create a limit order. When the price reaches this minimum tick, the LP position converts fully vGas, which can then be closed and transitioned into a Trade position. Since LP positions have reduced collateral requirements (no swap fees nor price impact on entry), this approach allows for the same vGas position with less collateral.

## Recommendation
Consider if this behavior should be prevented from a protocol perspective. One possible solution would be to fully close LP's position in _closeLiquidityPosition instead of the transition to Trade position, although low liquidity environments would have to be taken into consideration, and slippage protection would have to be appropriately handled.
