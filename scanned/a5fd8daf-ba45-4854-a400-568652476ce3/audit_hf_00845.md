# [M] M-18 | Pool Cap Can Be Bypassed

## Summary
Severity: Medium
Contest weight: 0.1423
Dataset id: 2581
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can deposit the pool's respective asset by calling the deposit function in the pool contract. The function allows the pool owner to enforce a pool cap; however, when an ERC777 asset is used, this limit can be bypassed. This issue arises because pool.totalAssets.assets is updated after the asset transfer, which is the point of reentrancy. A user can reenter with pool.totalAssets.assets not yet updated, so the limit check will use the old total asset value. For example, if the totalAssets are 10 tokens away from the cap, a user could initially deposit 10 tokens. During the asset transfer, the user can reenter the function and make a second deposit of 10 tokens. As a result, totalAssets will end up being 10 tokens over the limit.

## Proof of Concept
https://github.com/GuardianAudits/sentiment-team-2/blob/POC_BYPASS_POOL_CAP/test/guardian/pocs/bypassPoolCap.t.sol

## Recommendation
The asset transfer should be the initial step in the function to avoid a malicious state where tokens have not been transferred to the pool yet. Additionally, a nonReentrant modifier can be added to further secure the function.
