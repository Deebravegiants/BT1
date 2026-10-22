# [M] Improper Vault Proportion Update Upon Strategy Removal

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 13041
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Spool protocol has a user-facing Vault contract to support user deposits and withdrawals. The user deposits will be redirected to back-end strategies for yields. The strategies may be dynamically added or removed from the supported Vault. While analyzing the removal logic of a current strategy, we notice the current implementation needs to be corrected. To elaborate, we show below the related code snippet of the related notifyStrategyRemoved() routine, which will be called to notify a vault a strategy was removed from Spool. Speciﬁcally, when an active strategy is removed, there is a need to dynamically reallocate the funds from the removed strategy to other strategies. The dynamic reallocation is speciﬁed with the proportions for each strategy. Our analysis shows the resulting newProportions is not correct since it needs to start as 0, instead of being initialized to the stale _proportions (line 647)!
```solidity
function notifyStrategyRemoved(
    address[] memory vaultStrategies,
    uint256 i
) external
    reallocationFinished
    verifyStrategies(vaultStrategies)
    hasStrategies(vaultStrategies)
    redeemVaultStrategiesModifier(vaultStrategies)
{
    require(
        i < vaultStrategies.length &&
        !controller.validStrategy(vaultStrategies[i]),
        "BSTR"
    );
    uint256 lastElement = vaultStrategies.length - 1;
    address[] memory newStrategies = new address[](lastElement);
    if (lastElement > 0) {
        for (uint256 j; j < lastElement; j++) {
            newStrategies[j] = vaultStrategies[j];
        }
        if (i < lastElement) {
            newStrategies[i] = vaultStrategies[lastElement];
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
                newProportions = newProportions.set14BitUintByIndex(j, propJ);
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
    emit StrategyRemoved(i, vaultStrategies[i]);
}
```

## Recommendation
Correct the above logic to calculate the new reallocation newProportions when an active strategy is being removed.
