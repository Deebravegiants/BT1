# [M] TREC-3 | Unexpected Rewards

## Summary
Severity: Medium
Contest weight: 0.1006
Dataset id: 9329
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The allowance is used to determine how much WETH to inject into the Rewards system and it is incremented based on the current balance of the TransferReceiver. However the balance of the TransferReceiver can be inflated by transferring WETH directly to the TransferReceiver contract. Therefore rewards that are not explicitly from GMX are able to enter the Rewards system. Additionally, it is possible that privateTransferMode is turned off for either esGMX or bnGMX in the future, which could also potentially perturb the Rewards system.

## Recommendation
Consider if outside WETH should be included in the accounted rewards. If not, implement a before and after balance check when calling rewardRouter.handleRewards to get the actual WETH amount received from GMX. Additionally, have a plan for the scenario where privateTransferMode is turned off for either esGMX or bnGMX.
