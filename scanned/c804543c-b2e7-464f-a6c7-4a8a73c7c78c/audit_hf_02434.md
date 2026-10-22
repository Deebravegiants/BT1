# [M] Proper Strategy Removal Logic in notifyStrategyRemoved()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 13056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Spool is a middleware that connects users to existing and new yield generators and yield optimizers. Accordingly, the protocol has the flexible support of adding and removing external strategies. While reviewing the current strategy-removal logic, we notice the current implementation is flawed. To elaborate, we show below the related function, i.e., notifyStrategyRemoved(). When an existing strategy needs to be removed, there is a need to adjust the deposit proportions accordingly. However, the proportions-adjusting logic has a mis-calculation at line 610. The new proportions need to be updated with the iteration for all remaining strategies (j), instead of the one being removed (i). In other words, it does not update the proportions as intended!
```solidity
function notifyStrategyRemoved(
    address strat,
    address[] memory vaultStrategies,
    uint256 i
) external
    verifyStrategies(vaultStrategies)
    hasStrategies(vaultStrategies)
    redeemVaultStrategiesModifier(vaultStrategies)
{
    require(vaultStrategies[i] == strat, "NSTR");
    uint256 lastElement = vaultStrategies.length - 1;
    address[] memory newStrategies = new address[](lastElement);
    if (lastElement > 0) {
        for (uint256 j; j < lastElement; j++) {
            newStrategies[j] = vaultStrategies[j];
            if (i < lastElement) {
                newStrategies[i] = vaultStrategies[lastElement];
            }
        }
        uint256 _proportions = proportions;
        uint256 proportionsLeft = FULL_PERCENT - _proportions.get14BitUintByIndex(i);
        if (lastElement > 1 && proportionsLeft > 0) {
            if (i == lastElement) {
                _proportions = _proportions.reset14BitUintByIndex(i);
            } else {
                uint256 lastProportion = _proportions.get14BitUintByIndex(lastElement);
                _proportions = _proportions.reset14BitUintByIndex(i);
                _proportions = _proportions.set14BitUintByIndex(i, lastProportion);
            }
            uint256 newProportions = _proportions;
            uint256 lastNewElement = lastElement - 1;
            uint256 newProportionsLeft = FULL_PERCENT;
            for (uint256 j; j < lastNewElement; j++) {
                uint256 propJ = _proportions.get14BitUintByIndex(j);
                propJ = (propJ * FULL_PERCENT) / proportionsLeft;
                newProportions = newProportions.set14BitUintByIndex(i, propJ);
                newProportionsLeft -= propJ;
            }
            newProportions = newProportions.set14BitUintByIndex(lastNewElement, newProportionsLeft);
            proportions = newProportions;
        } else {
            proportions = FULL_PERCENT;
        }
    } else {
        proportions = 0;
    }
    _updateStrategiesHash(newStrategies);
}
```

## Recommendation
Properly adjust the proportions when there is a need to remove an existing strategy.
