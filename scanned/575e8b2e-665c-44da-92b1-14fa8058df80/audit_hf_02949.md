# [M] No slippage application in the _swapToVolt function

## Summary
Severity: Medium
Contest weight: 0.1782
Dataset id: 16365
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _swapToVolt function has no slippage applied (uint256 amountOutMin = 0;). This function is used within the collectFees function and the swapToVoltOnly which is desired for the privileged account. The lack of slippage control can lead directly to the sandwich attacks. /// @notice Swap `amountIn` amount of `tokenIn` ERC-20 tokens to `$VOLT` token (represented by `voltToken`) /// @dev The swap happens according to `VoltSwapRouterConfig` set for `tokenId` if (amountIn == 0) return; PositionManagerInvalidErc20Token(); if (tokenIn == tokenOut) revert PositionManagerInvalidErc20Token(); VoltSwapRouterConfig memory config = _voltSwapRouterConfigs[tokenIn]; // There is no slippage control uint256 amountOutMin = 0; if (config.routerType == VoltSwapRouterType.UniV2) { _setAllowanceMaxIfNeeded(IERC20(tokenIn), amountIn, _swapUniV2(IRouterV2(router), tokenIn, tokenOut, amountIn, amountOutMin); } else if (config.routerType == VoltSwapRouterType.UniV3) { uint24 feeTier = config.feeTier; if (feeTier == 0) revert PositionManagerInvariant("fee tier"); _setAllowanceMaxIfNeeded(IERC20(tokenIn), amountIn, _swapUniV3(IRouterV3(router), tokenIn, tokenOut, amountIn, amountOutMin, feeTier); } else { revert PositionManagerInvariant("router type"); VoltStakingReport.md

## Recommendation
Consider enhancing the _swapToVolt function by introducing slippage, that provided by the user as input is preventing large deviation within the pair's swap.
