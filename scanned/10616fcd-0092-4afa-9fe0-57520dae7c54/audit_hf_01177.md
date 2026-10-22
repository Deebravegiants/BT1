# [M] Mispricing at Bonding Curve Terminal Due to Incorrect Price Approximation

## Summary
Severity: Medium
Contest weight: 0.7041
Dataset id: 5048
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Agent contract, the bonding curve implements a price function that asymptotically approaches infinity as token supply is depleted. Mathematically:  
P(x) = (a / (D − x − o + 1)) · P0  
Where:  
• x is the number of tokens sold (or the complement of current balance).  
• a = CURVE_NUMERATOR.  
• D = CURVE_DENOMINATOR.  
• o = CURVE_OFFSET.  
• P_0 = initialPrice.  
As x → D, the denominator of the curve approaches zero, and the price diverges toward infinity. However, in the current Solidity implementation, calculatePrice(0) — which represents the case where all tokens are sold (i.e., currentBalance == 0) — returns a capped value such as initialPrice * 1000.  
This approximation introduces significant inaccuracies during high-end curve interactions, especially for large buy operations nearing full supply depletion. While this is meant as a safety fallback to avoid division-by-zero, it results in the following issue:  
• The price at full supply (P(D - 1)) should be:  
P(D − 1) = (35,190,005,730 / (-32 + 1)) · P0 = 35,190,005,699 · P0  
• But the contract may return:  
P(0) = 1000 · P0.  
This results in a mispriced endPrice during calculateAveragePrice() calls for buys close to terminal supply, severely undervaluing tokens and breaking the intended convex price dynamics of the bonding curve.  
Given that the average price formula for buys is:  
Pavg = Pstart + 3 · Pend  
If P_end is incorrectly capped, the resulting P_avg is significantly lower than expected, allowing users to purchase tokens below their intended cost. The issue is amplified due to the buy-weighted averaging favoring endPrice.  
Exploitation Scenario:  
1. A buyer targets a moment when the remaining token supply is minimal.  
2. tokenAmount pushes endBalance = 0.  
3. calculatePrice(0) returns initialPrice * 1000 rather than the mathematically correct terminal value (~$35B).  
4. averagePrice is vastly under-calculated.  
5. The buyer receives tokens at a deep discount.  
6. If LP creation hasn't occurred yet (or is delayed), the user can resell those tokens through the curve or other mechanisms, profiting from the mispricing.  
Mitigations and Friction Points:  
• The buyToken function checks:  
```solidity
scaledTokensSoldPercentage + scaledNewTokensPercentage < CURVE_DENOMINATOR * PRECISION;
```  
This may not be a sufficient boundary, as it incorrectly uses CURVE_DENOMINATOR instead of 1 * PRECISION, failing to prevent x → D edge conditions.  
• The isMarketCapReached() function typically finalizes the curve by triggering LP creation before this scenario manifests, acting as a strong preventative layer.  
• Additionally, the sellPenalty mechanism discourages arbitrage unless the market deviates by 10% or more, providing an additional disincentive in many practical cases.

Impact Explanation:  
High, because if a user manages to purchase tokens at the terminal end of the bonding curve and receives them at a mispriced average (far below intended value), it could result in extractable economic value and undermine the curve’s integrity. This breaks the expected cost gradient of the curve and could be exploited to drain protocol value under precise timing or adversarial automation.

## Recommendation
To fix the mispricing at the end of the bonding curve, the logic in calculatePrice(0) should be updated to accurately reflect the theoretical price when all tokens are sold, rather than returning a hardcoded value like initialPrice * 1000. This can be achieved in two ways.  
One option is to simulate the final step of the curve by substituting x = CURVE_DENOMINATOR - 1, which avoids division by zero but still provides a very close approximation to the true terminal price. This keeps the formula aligned with the actual curve shape and ensures accurate pricing:  
```solidity
if (currentBalance == 0) {
    uint256 simulatedX = CURVE_DENOMINATOR - 1;
    uint256 rawPrice = (CURVE_NUMERATOR * PRECISION) / (CURVE_DENOMINATOR - simulatedX);
    uint256 finalPrice = rawPrice > CURVE_OFFSET * PRECISION
        ? rawPrice - (CURVE_OFFSET * PRECISION) + PRECISION
        : PRECISION;
    return (finalPrice * initialPrice) / PRECISION;
}
```  
Alternatively, for gas optimization and simplicity, the correct multiplier can be precomputed and hardcoded. Since the terminal price converges to:  
P_terminal = (CURVE_NUMERATOR - (CURVE_OFFSET - 1)) * initialPrice  
= 35_190_005_699 * initialPrice  
you can directly return:  
```solidity
if (currentBalance == 0) {
    return initialPrice * 35_190_005_699;
}
```  
Both approaches resolve the underpricing issue while preserving the integrity of the bonding curve mechanics.
