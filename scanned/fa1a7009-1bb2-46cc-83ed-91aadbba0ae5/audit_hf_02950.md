# [M] No slippage application in the _addLiquidityUniV3 function

## Summary
Severity: Medium
Contest weight: 0.1592
Dataset id: 16366
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _addLiquidityUniV3 function has no slippage applied (amount0Min: 0, amount1Min: 0,). This function is used only within the addLiquidity which is desired for the privileged account. The adding liquidity process within the Uniswapv3 is prone to the sandwich attacks, as it is stated in the documentation: In production, amount0Min and amount1Min should be adjusted to create slippage protections. function _addLiquidityUniV3(uint256 tokenId, uint256 amountAdd0, uint256 amountAdd1) internal returns (uint128 liquidity, uint256 amount0, uint256 amount1) UniV3Nft memory nft = _getNftUniV3(tokenId); _setAllowanceMaxIfNeeded(IERC20(nft.token0), amountAdd0, _setAllowanceMaxIfNeeded(IERC20(nft.token1), amountAdd1, INonfungiblePositionManager.IncreaseLiquidityParams memory params = INonfungiblePositionManager .IncreaseLiquidityParams({ tokenId: tokenId, amount0Desired: amountAdd0, amount1Desired: amountAdd1, amount0Min: 0, amount1Min: 0, deadline: block.timestamp (liquidity, amount0, amount1) = VoltStakingReport.md nftManager.increaseLiquidity(params); //@audit allowance not reduced

## Recommendation
Consider enhancing the _addLiquidityUniV3 function by introducing slippage, that provided by the user as input is preventing large deviation within the pair's swap.
