# [M] Owner can circumvent allowance() via enableTradingWithWeights()

## Summary
Severity: Medium
Contest weight: 0.4094
Dataset id: 8437
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The vault Owner can set arbitrary weights via disableTrading() and then call enableTradingWithWeights() to set the spot price and create arbitrage opportunities for himself. This way allowance() in withdraw() checks, which limit the amount of funds an owner can withdraw, can be circumvented.
Something similar can be done with enableTradingRiskingArbitrage() in combination with sufficient time.
Also see the following issues:
• allowance() doesn’t limit withdraw()s
• enableTradingWithWeights allow the Treasury to change the pool’s weights even if the swap is not disabled
• Separation of concerns Owner and Manager
function disableTrading() ... onlyOwnerOrManager ... {
setSwapEnabled(false);
}
function enableTradingWithWeights(uint256[] calldata weights) ... onlyOwner ... {
...
pool.updateWeightsGradually(timestamp, timestamp, weights);
setSwapEnabled(true);
}
function enableTradingRiskingArbitrage() ... onlyOwner ... {
setSwapEnabled(true);
}
```

## Recommendation
Consider allowing only the manager to execute the disableTrading() function although this also has disadvantages. Additionally, use an oracle to determine spot price (as is already envisioned for the next versions of the protocol).
