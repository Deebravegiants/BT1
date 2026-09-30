# [H] In PCLBaseSwapInside::_compoundRewards(), if the sellPortion is smaller than rewardSwapThreshold, some of the rewards will move to keepPortion

## Summary
Severity: High
Contest weight: 0.1541
Dataset id: 6528
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Rewards allocated to compounding shares are only swapped to tokens 0 and 1 if the sellPortion exceeds the rewardSwapThreshold. However, the allocated sell portion is not accounted for anywhere, which means that if the rewards are not sold due to being smaller than the threshold, a portion of them will go to the keepPortion the next time _compoundRewards() is called.
In the worst scenario, sell portion may always be smaller than the threshold if _compoundRewards() is called frequently enough and no rewards will be allocated to compounding shares.

## Recommendation
Add a variable tracking the sell portion to make sure rewards never transition to the keep portion.
