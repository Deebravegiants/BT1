# [M] Suggested Use Of Safemath In init()

## Summary
Severity: Medium
Contest weight: 0.4315
Dataset id: 13035
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SorbettoFragola protocol allows the governance to set the tickLower and tickUpper for investors when they try to provide the liquidity in the pool. With that, the protocol retrieves the currentTick, adds the baseThreshold to compute the tickUpper, and subtracts the baseThreshold to compute the tickLower. And the protocol uses the tickRangeMultiplier set by the governance to multiply the tickSpacing to get the baseThreshold. During our analysis, we notice potential overflow and underflow issues in the above calculation. In the following, we list the related init() function.
```solidity
function init() external onlyGovernance {
    require(!finalized, "F");
    finalized = true;
    int24 baseThreshold = tickSpacing * ISorbettoStrategy(strategy).tickRangeMultiplier();
    (uint160 sqrtPriceX96, int24 currentTick,,,,,,) = pool03.slot0();
    int24 tickFloor = PoolVariables.floor(currentTick, tickSpacing);
    tickLower = tickFloor - baseThreshold;
    tickUpper = tickFloor + baseThreshold;
    universalMultiplier = PriceMath.token0ValuePrice(sqrtPriceX96, token0DecimalPower);
}
```
The problem is introduced when the multiplication of tickSpacing and tickRangeMultiplier is larger than 24 bits, which leads to an overflow. Besides, when calculating tickLower and tickUpper, if the tickFloor is smaller than the baseThreshold, an underflow occurs. And if the sum of tickFloor and baseThreshold is large enough, an overflow occurs.

## Recommendation
Use Safemath for all the calculations in the above init() function.
