# [H] H-05 | Rewards Are Lost For aspToken

## Summary
Severity: High
Contest weight: 0.1756
Dataset id: 22162
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users stake their LP tokens because spTokens accrue rewards in different tokens. The criteria for such a token is to either be a part of the whitelisted ones or be the specified token for the given TokenRewards contract. When spTokens are deposited to aspTokens, the AutoCompondingPodLp contract receives the rewards and uses _processRewardsToPodLp to convert them to new spTokens. However, it does so only for the whitelisted tokens and ignores the specific reward token for the TokenRewards. In result, any rewards accumulated in the specific token that is not part of the whitelisted tokens will not be correctly distributed to the holders of the aspTokens.

## Recommendation
In addition to the whitelisted tokens collect the rewards from the rewardsToken as well.
