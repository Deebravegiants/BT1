# [M] Farming Amount Limit

## Summary
Severity: Medium
Contest weight: 0.2191
Dataset id: 14744
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FarmAccounting contract is used by the Farm contract to handle computation on Info. The Farm contract works closely with the ERC20Farmable contract to create a token system with farming capability.
The startFarming() function in FarmAccounting contract is used by the reward distributor to start the farming session.
This function requires the input amount to be at most uint176 (based on a check on line [32]).
However, there is an edge case where this requirement is incorrect when calculating farmedPerToken (FPT) value computed by ERC20Farmable.farmedPerToken(). The edge case occurs when FarmAccounting.Info.reward is sufficiently high and the period since the last checkpoint is sufficiently long, causing FarmAccounting.farmedSinceCheckpointScaled() to return a value higher than 1e54 and ERC20Farmable_lazyGetFarmed() to return zero. As a result, the accounting of the farming distributions is incorrect and participants receive less than they are owed.
This means that the safe value for farming depends on elapsed, reward, and duration as identified in FarmAccounting.farmedSinceCheckpointScaled() (line [19]), where the result should not be more than 1e54 at all times, based on the check done in function ERC20Farmable._lazyGetFarmed() (line [153]). This indicates that the safest maximum value for farming amount to avoid this edge case is 1e36.
The issue can be prevented by calling Farm.startFarming() to enforce a frequent checkpoint update. However, once the farming period passes, this method no longer works.

## Recommendation
The check in FarmAccounting.startFarming() should be changed from uint176 to 1e36. This will mitigate the issue.
Alternatively, make sure this behaviour is understood. Precalculating reward amounts and farming periods before starting the farming session, in addition to regularly enforcing a checkpoint update can help prevent this edge case.
The testing team also recommends providing a safety measure such that the reward token can be retrieved if anything goes wrong after the end of a farming session.
