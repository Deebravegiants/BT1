# [M] Broken invariant : the sum of all (delegateRewardsPerShare * delegated stake - reward debt) = the balance of the /x/bank AlloraPendingRewardForDelegatorAccountName module account when when distributing delegate stakers rewards

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-06-allora
Published: 2024-07-19
Source: https://github.com/sherlock-audit/2024-06-allora-judging/issues/129
Type: sherlock-finding

## Details
imsrybr0

Medium

# Broken invariant : the sum of all (delegateRewardsPerShare * delegated stake - reward debt) = the balance of the /x/bank AlloraPendingRewardForDelegatorAccountName module account when when distributing delegate stakers rewards

## Summary
Broken invariant : the sum of all (delegateRewardsPerShare * delegated stake - reward debt) = the balance of the /x/bank AlloraPendingRewardForDelegatorAccountName module account when distributing delegate stakers rewards

## Vulnerability Detail
When distributing delegate stakers, the reward debt in increased by the full untrimmed amount while only the trimmed amount is sent to the delegate staker.

Additionally, if the pending reward amount is less than 1, the reward debt will still be increased while no rewards are sent.

## Impact
AlloraPendingRewardForDelegatorAccountName will end up holding more than the amount owed.

## Code Snippet
[RewardDelegateStake](https://github.com/sherlock-audit/2024-06-allora/blob/main/allora-chain/x/emissions/keeper/msgserver/msg_server_stake.go#L270-L309)
```golang
func (ms msgServer) RewardDelegateStake(ctx context.Context, msg *types.MsgRewardDelegateStake) (*types.MsgRewardDelegateStakeResponse, error) {
	// Check the target reputer exists and is registered
	isRegistered, err := ms.k.IsReputerRegisteredInTopic(ctx, msg.TopicId, msg.Reputer)
	if err != nil {
		return nil, err
	}
	if !isRegistered {
		return nil, types.ErrAddressIsNotRegisteredInThisTopic
	}

	delegateInfo, err := ms.k.GetDelegateStakePlacement(ctx, msg.TopicId, msg.Sender, msg.Reputer)
	if err != nil {
		return nil, err
	}
	share, err := ms.k.GetDelegateRewardPerShare(ctx, msg.TopicId, msg.Reputer)
	if err != nil {
		return nil, err
	}
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2024-06-allora-judging/issues/129_
