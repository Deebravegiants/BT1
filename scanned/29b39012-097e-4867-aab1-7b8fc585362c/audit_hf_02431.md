# [M] Incorrect Strategies Hash Update in _removeStrategyCalldata()

## Summary
Severity: Medium
Contest weight: 0.4202
Dataset id: 13042
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Spool protocol has a Controller contract that is the central point of the protocol for assessing the validity of various data in the system (i.e. supported strategy, vault etc.). While reviewing the current logic to remove an existing strategy, we notice its current logic needs to be corrected. In particular, an issue stems from the need to properly update the strategiesHash since an existing strategy is being removed. However, the hash-update logic (line 599) fails to use the updated strategies to compute the hash. Instead, it still uses the stale list to compute and update the strategiesHash. Unfortunately, an incorrect strategiesHash may fail a variety of reallocation routines.
```solidity
function _removeStrategyCalldata(address[] calldata allStrategies, address strategy) private {
    uint256 lastEntry = allStrategies.length - 1;
    address[] memory newStrategies = allStrategies[0: lastEntry];
    for (uint256 i = 0; i < lastEntry; i++) {
        if (allStrategies[i] == strategy) {
            strategies[i] = allStrategies[lastEntry];
            newStrategies[i] = allStrategies[lastEntry];
            break;
        }
    }
    strategies.pop();
    _updateStrategiesHash(allStrategies);
}
```

## Recommendation
Correct the above logic in the update of strategiesHash when an existing strategy is being removed.
