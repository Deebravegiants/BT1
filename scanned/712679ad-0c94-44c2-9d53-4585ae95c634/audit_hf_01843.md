# [M] twapAmount can be manipulated to increase slippage tolerance for all buy actions

## Summary
Severity: Medium
Contest weight: 0.1950
Dataset id: 10255
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SwapActions.getTwapAmount is used in swapExactInput to compute calculated TWAP and slippage values for a minimum amount to be used as slippage protection in the UniswapV3 SwapRouter, in case the minAmountOut function input is zero. (uint256 twapAmount, uint224 slippage) = getTwapAmount(tokenIn, tokenOut, tokenInAmount); uint256 minAmount = minAmountOut == 0 ? wmul(twapAmount, slippage) : minAmountOut; The TWAP amount is retrieved using the oldest observation, which relies on the slippageConfig.twapLookback configuration in storage. Even though a TWAP delivers more resilience against price manipulation than a spot price, it can still be manipulated if the attacker endures the spot price manipulation for the duration of the used TWAP window. Therefore, this value is not safe to be used to calculate slippage tolerances on the fly. While the price of sustaining such a price manipulation increases with the lookback duration, it is still quite possible to achieve for large liquidity holders, especially in low liquidity situations or when the window is sufficiently small (the default here is 15 minutes). This affects all functions calling swapExactInput with minAmountOut set to 0, which are all buy actions. The manipulated slippage tolerance could later be used to extract value from all swaps for a meaningful period of time (until the attacker can no longer sustain the manipulation with profit or until the TWAP goes back to its normal price).

## Recommendation
Consider removing the usage of a calculated slippage based on a TWAP value.
