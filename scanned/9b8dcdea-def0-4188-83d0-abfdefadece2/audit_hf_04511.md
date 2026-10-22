# [H] H-04 | Exact Input Amount May Not Be Used

## Summary
Severity: High
Contest weight: 0.2972
Dataset id: 22074
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the SwapRouter.exactInputSingle function in Uniswap V3, the exact amountIn is not guaranteed to always be used. If the sqrtPriceLimitX96 is hit during the swap then the swap will complete and the exactInputSingle function call will pass. https://github.com/Uniswap/v3-periphery/blob/0682387198a24c7cd63566a2c58398533860a5d1/contracts/SwapRouter.sol#L199 https://github.com/Uniswap/v3-periphery/blob/0682387198a24c7cd63566a2c58398533860a5d1/contracts/SwapRouter.sol#L87 A sqrtPriceLimitX96 of 0 is used in the EpochTradeModule.swapTokensExactIn function, therefore the sqrtPriceLimitX96 is assigned to roughly the min or max tick upon performing the actual swap. This means if the swap are to go outside of the range of valid prices for the epoch the exact input amount will not be entirely used up. In the context of a short, this can mean an overestimation of the amount borrowed which was not entirely used for the swap and causes immediate loss for the user. This is not an issue for the exactOutputSingle function as the amountOutReceived is validated to be exactly the amountOut: https://github.com/Uniswap/v3-periphery/blob/0682387198a24c7cd63566a2c58398533860a5d1/contracts/SwapRouter.sol#L199.

## Recommendation
There are a number of ways this edge case can be validated against:
• Consider reverting if the price of the Uniswap pool is outside of the valid range after a swap, or as an invariant check after all functions which interact with Uniswap.
• Consider validating whether the swap would put price outside of the valid range, and either reverting or using a partial fill if this is the case.
• Consider reverting if the balance used up by the swap is not exactly the amount specified, measured by the balance of address(this).
