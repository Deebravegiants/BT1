# [C] C-02 | Compounding Of Rewards To LP Failure

## Summary
Severity: Critical
Contest weight: 0.2868
Dataset id: 22155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function _processRewardsToPodLp is called on every major flow such as deposit and withdrawal to compound any earned rewards to the LP token and back into the AutoCompoundingPodLp. The amounts passed to indexUtils.addLPAndStake will be the entire balance of POD in the AutoCompoundingPodLp, and half of the paired lp token that’s obtained from the reward tokens with a V3 swap. The issue is that the token A and token B amounts can be wildly different from their current reserve ratio in the pool, causing the desired token inputs to fail the calculated amountAMin and amountBMin passed to Uniswap V2. There can be a multitude of reasons why few paired LP tokens are to be added, such as small reward distribution since the last reward claim and/or V3 swap manipulation in swapV3Single since 0 slippage is passed. An attacker is not necessary for the UniV2 revert to occur. Attackers can also inflate the balances with token donations to trigger this revert as well. This DoS will occur even if LP_SLIPPAGE was drastically increased. Ultimately, all core functionalities of the AutoCompoundingPodLp can be prevented, and users can lose assets due to the inability to withdraw.

## Recommendation
In _pairedLpTokenToPodLp, consider performing some sanity checks to ensure tokens are in the correct ratio before calling IndexUtils.addLPAndStake. Furthermore, considering wrapping the auto-compounding in a try-catch.
