# [M] Rewards are not rolled over

## Summary
Severity: Medium
Contest weight: 0.1504
Dataset id: 16907
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a reward‑rollover bug in the staking contract’s accounting logic. The contract calculates a per‑second reward rate when an admin calls the notifyRewardAmount function, but the amount of reward that should be credited to stakers is only distributed when there is a non‑zero total supply of deposited tokens. If the contract has been started (startTime set) and there is a period during which no user has deposited any tokens, the reward rate still accrues, yet the internal accounting does not record any earned reward because the total supply is zero. Consequently, the rewards that technically belong to that time window are never attributed to any future staker and remain in the contract’s balance as “unused” tokens. This situation can be reproduced by (1) an admin setting a rewardRate of 10 tokens per second, (2) having no deposits for the first 10 seconds, and (3) later depositing tokens; the 100 tokens that should have been earned during the idle period stay locked in the contract. The impact is a loss of economic value: the protocol’s incentive model is broken, users who eventually stake never receive the rewards they expect, and the token balance appears idle, misleading observers. The issue primarily affects token holders who intend to earn rewards, the protocol’s accounting integrity, and any parties relying on the advertised reward distribution. It occurs whenever the contract experiences a zero‑stake interval after deployment, which is a realistic scenario for new or low‑traffic deployments. The problem was uncovered during a formal audit by Code4rena, where the auditors observed that the contract’s sweeper function could withdraw the stranded reward tokens, but noted that removing the sweeper (as suggested by a related finding) would make the loss permanent. The bug is subtle because the contract’s external view may show a healthy reward balance, yet no accounting entry ever moves those tokens to users, making the deficiency easy to miss in routine testing that only checks post‑deposit reward accrual. The class of bug belongs to reward‑allocation or accounting rollover errors, where accrued value is not carried forward across state changes. From a user’s perspective, the expected behavior is that after depositing they receive a proportionate portion of all rewards since the contract’s start; in reality they may see their balance stay at zero or receive less than anticipated, leading to confusion or distrust. To remediate the issue the contract should, on the first deposit (or any deposit after a zero‑supply period), compute the elapsed time since startTime, multiply it by the current rewardRate, and credit that amount as “unused” rewards that can be rolled into the next notifyRewardAmount calculation, ensuring no reward value is ever lost. This conceptual fix restores continuity of reward accounting and aligns the contract’s behavior with its economic promises.

## Proof of Concept
1. Admin has added reward which made reward rate as 10 reward per second using notifyRewardAmount function

    rewardRate = reward.div(rewardsDuration);

2. For initial 10 seconds there were no deposits which means total supply was 0
3. So no reward were distributed for initial 10 seconds and reward for this duration which is `10*10=100` will remain in contract
4. Since on notifying contract of new rewards, these stuck rewards are not considered, these 100 rewards will remain in contract with no usage

## Recommendation
On very first deposit, better to have (block.timestamp-startTime) * rewardRate amount of reward being marked unused which can be used in next notifyrewardamount.

I see this as protocol leaked value since the rewards would be “lost” and isn’t attributed to anyone. 

Currently, the sweeper function allows the reward token to be withdrawn, thus providing a form of recovery. However, [#49](https://github.com/code-423n4/2022-09-y2k-finance-findings/issues/49) and its dups points out that this is a vuln, and if fixed, will remove this recovery.
