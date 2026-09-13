# [M] 5.3.1 Owner can circumventallowance()viaenableTradingWithWeights()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** AeraVaultV1.sol#L564-L
**Description:** The vault Owner can set arbitrary weights viadisableTrading()and then callenableTrading-
WithWeights()to set the spot price and create arbitrage opportunities for himself. This wayallowance()in
withdraw()checks, which limit the amount of funds an owner can withdraw, can be circumvented.
Something similar can be done withenableTradingRiskingArbitrage()in combination with sufficient time.
Also see the following issues:

- allowance()doesn’t limitwithdraw()s
- enableTradingWithWeightsallow the Treasury to change the pool’s weights even if the swap is not disabled
- Separation of concerns Owner and Manager
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


**Recommendation:** Consider allowing only the manager to execute thedisableTrading()function although this
also has disadvantages. Additionally, use an oracle to determine spot price (as is already envisioned for the next
versions of the protocol).
**Gauntlet:** For safety reasons we want the treasury to have full control over trading. Given our current trust model,
this is won’t be an issue for V1 so no action will be taken at this time.
**Spearbit:** Acknowledged.
