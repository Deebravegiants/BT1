# [M] Swap deadline set to block.timestamp provides no protection

## Summary
Severity: Medium
Contest weight: 0.2004
Dataset id: 16369
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the PositionManager contract, swaps are executed using either the Uniswap V2 or V3 router, depending on the configuration. When a swap is executed via Uniswap V2 router, the deadline parameter, which should ensure that transactions expire after a certain time, is incorrectly set to block.timestamp: function _swapUniV2( IRouterV2 _router, uint256 amountIn, uint256 amountOutMinimum ) internal { _router.swapExactTokensForTokensSupportingFeeOnTransferTokens( block.timestamp Since block.timestamp represents the current block time, it does not provide any protection against delayed or stale transaction execution. This means: Transactions stuck in the mempool can be executed at any future time when the price has changed significantly. If the transaction is executed later due to network congestion, the received token amount may be much lower than expected, leading to funds loss. Same issue exists when adding liquidity to an existing deposited UniV3 liquidity position: function _addLiquidityUniV3(uint256 tokenId, uint256 amountAdd0, uint256 amountAdd1) internal returns (uint128 liquidity, uint256 amount0, uint256 amount1) VoltStakingReport.md INonfungiblePositionManager.IncreaseLiquidityParams memory params = INonfungiblePositionManager .IncreaseLiquidityParams({ tokenId: tokenId, amount0Desired: amountAdd0, amount1Desired: amountAdd1, amount0Min: 0, amount1Min: 0, deadline: block.timestamp (liquidity, amount0, amount1) = nftManager.increaseLiquidity(params);

## Recommendation
Instead of hardcoding block.timestamp as the deadline, introduce a caller-specified deadline parameter to ensure that the swap is executed within an acceptable timeframe.
