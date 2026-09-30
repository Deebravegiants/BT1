# [C] Inﬁnite Loop In _getSelfDelegations()

## Summary
Severity: Critical
Contest weight: 0.5849
Dataset id: 15100
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _getSelfDelegations() function can suﬀer from an inﬁnite loop if the operator has staked in a strategy that is not included in the _strategyParams array. This causes syncWithOmni() to fail if any operator has staked in an incompatible strategy. ```solidity
for (uint256 i = 0; i < strategies.length;) {
    IStrategy strat = strategies[i];
    // find the strategy params for the strategy
    StrategyParam memory params;
    for (uint256 j = 0; j < _strategyParams.length;) {
        if (address(_strategyParams[j].strategy) == address(strat)) {
            params = _strategyParams[j];
            break;
        }
        unchecked {
            // if strategy is not found, do not consider it in stake
            if (address(params.strategy) == address(0)) continue;
            staked += _weight(shares[i], params.multiplier);
        }
    }
}
```
If the current strategy is not found inside _strategyParams in line [567], the outer for-loop will continue without incrementing the i iterator and the same incompatible strategy will be checked indeﬁnitely until the transaction runs out of gas.

## Recommendation
There are two proposed solutions to resolve the issue. 1. Move i++ into the for-loop header in line [551] 2. Increment i inside the if-block before the continue keyword in line [567].
