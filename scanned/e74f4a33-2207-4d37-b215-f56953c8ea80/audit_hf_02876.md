# [M] Amounts to distribute are added directly to tokenPerShare, skipping using rewardPerToken

## Summary
Severity: Medium
Contest weight: 0.0636
Dataset id: 16155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Rewards are emitted at a rate of rewardTokenPerBlock. However, when distributing, the received reward tokens are added directly to rewardPerToken, instead of being left in the contract and letting rewardTokenPerBlock distribute the amounts over time.

## Recommendation
Don't add the amount to swap to amountToDistribute, but let the tokens in the contract so rewards can be emitted according to rewardTokenPerBlock. In fact, the swap should be performed before calculating emittedRewards(), so it does not happen that the tokens to distribute are cropped due to not having enough balance and then due to the swap there is now balance.
