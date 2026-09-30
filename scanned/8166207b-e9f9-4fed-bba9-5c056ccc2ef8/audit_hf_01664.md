# [H] MultiplierContract::proposeMultipleUpdates() updates maxLevel before executing the update

## Summary
Severity: High
Contest weight: 0.2302
Dataset id: 9012
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
MultiplierContract::proposeMultipleUpdates() updates maxLevel without going through the UPDATE_INTERVAL, which will affect the multiplier MultiplierContract::getMultiplier() right away, without updating the actual thresholds and multipliers.
If maxLevel >= prevMaxLevel, it still works correctly in MultiplierContract::getMultiplier() as the levels after prevMaxLevel will not yet have been created so the loop will just continue if (levelThresholds[i] == 0) continue;.
However, if maxLevel < prevMaxLevel, some of the previous levels will be skipped as soon as MultiplierContract::proposeMultipleUpdates() is called. For example, if there were 5 levels, but now just 4, if users were eligible for level 5, the maximum they can get is level 4, although MultiplierContract::executeUpdates().
Lastly, MultiplierContract::cancelUpdate() does not revert the maxLevel update in MultiplierContract::proposeMultipleUpdates(), even though the update was cancelled.

## Recommendation
The maxLevel should be updated only when MultiplierContract::executeUpdates() is called.
