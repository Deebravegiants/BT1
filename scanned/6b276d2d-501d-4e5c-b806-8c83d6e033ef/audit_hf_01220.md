# [M] addLiquidityCurve rateLimit miscalculation for Curve pool N > 2 enables partial limit bypass

## Summary
Severity: Medium
Contest weight: 0.2494
Dataset id: 5471
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The fix review version included a new rateLimit decrease in the addLiquidityCurve function where this finding has occurred. If the depositAmounts for an add_liquidity Curve call are not equally distributed, internally in Curve a swap happens to equalize the depositAmounts.
For example, if in a balanced pool with enough liquidity the depositAmounts are depositAmounts=[100, 10]. The total value added would be 110, and 45 units of token1 would be sold for 45 units of token2 to achieve an equal balance of 55 for both.
In the MainnetController.addLiquidityCurve, the rateLimit for addLiquidity is decreased after a call which limits the volume a relayer can use. In the new version, an additional rateLimit decrease for swapCurve has been added to addLiquidityCurve to adjust the rateLimit if the unequal depositAmounts result effectively in a swap.
This is achieved by the following logic:
// Compute the average swap value by taking the difference of the current underlying
// asset values from minted shares vs the deposited funds, and decrease the swap
// rate limit by this amount.
uint256 totalSwapped;
for (uint256 i; i < depositAmounts.length; i++) {
    totalSwapped += _absSubtraction(
        curvePool.balances(i) * rates[i] * shares / curvePool.totalSupply(),
        depositAmounts[i] * rates[i]
    );
}
uint256 averageSwap = totalSwapped / depositAmounts.length / 1e18;
rateLimits.triggerRateLimitDecrease(
    RateLimitHelpers.makeAssetKey(LIMIT_CURVE_SWAP, pool),
    averageSwap
);
The totalSwapped is basically the absolute difference between the initial depositAmounts provided by the relayer and the actual new depositAmounts in the Curve pool after the internal swap.
The update for the rateLimit should be the same amount as if the tokens would have been sold before by calling swapCurve to achieve an equal distribution in depositAmounts.
Dividing the totalSwapped by the depositAmounts.length is incorrect if there are more than two tokens in the pool. The totalSwapped, based on the absolute difference, is basically twice the sum of sold tokens.
Therefore, it is only required to divide the totalSwapped by 2.
• Example with three tokens:
Input
depositAmounts = [150, 30, 60]
totalValue = $240
Curve
equally balanced at = [80, 80, 80]
the effective swap would be = [-70, +50, +20]
MainnetController
totalSwapped = 150 - 80 + 80 - 30 + 80 - 60;
totalSwapped = 70 + 50 + 20;
totalSwapped = 140;
averageSwap = 46.66;
However, the averageSwap = 46.66 is not correct. The reasoning for this suggested change is that the update of the rateLimit - LIMIT_CURVE_SWAP should be the same as if the relayer were to first call swapCurve themselves and then call addLiquidity with an even distribution. For the example above depositAmounts = [150, 30, 60], this would be as if two sells of tokenIdx=0 would happen:
• swapCurve:
– inputIndex: 0.
– outputIndex: 1.
– amountIn: 50.
• swapCurve:
– inputIndex: 0.
– outputIndex: 2.
– amountIn: 20.

## Recommendation
The correct calculation for the approximated update should be:
- uint256 averageSwap = totalSwapped / depositAmounts.length / 1e18;
+ uint256 effectiveSwap = totalSwapped / 2 / 1e18;
