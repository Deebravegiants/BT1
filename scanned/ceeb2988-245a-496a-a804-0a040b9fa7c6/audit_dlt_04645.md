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
	pendingReward, err := delegateInfo.Amount.Mul(share)
	if err != nil {
		return nil, err
	}
	pendingReward, err = pendingReward.Sub(delegateInfo.RewardDebt)
	if err != nil {
		return nil, err
	}
	if pendingReward.Gt(alloraMath.NewDecFromInt64(0)) { // <===== Audit
		coins := sdk.NewCoins(sdk.NewCoin(params.DefaultBondDenom, pendingReward.SdkIntTrim())) // <===== Audit : Only send the trimmed pending reward amount
		err = ms.k.SendCoinsFromModuleToAccount(ctx, types.AlloraPendingRewardForDelegatorAccountName, msg.Sender, coins)
		if err != nil {
			return nil, err
		}
		delegateInfo.RewardDebt, err = delegateInfo.Amount.Mul(share)  // <===== Audit : Increases by the untrimmed pending reward amount
		if err != nil {
			return nil, err
		}
		ms.k.SetDelegateStakePlacement(ctx, msg.TopicId, msg.Sender, msg.Reputer, delegateInfo)
	}
	return &types.MsgRewardDelegateStakeResponse{}, nil
}
```

[](https://github.com/sherlock-audit/2024-06-allora/blob/main/allora-chain/x/emissions/keeper/keeper.go#L931-L1072)
```golang
func (k *Keeper) RemoveDelegateStake(
	ctx context.Context,
	blockHeight BlockHeight,
	topicId TopicId,
	delegator ActorId,
	reputer ActorId,
	stakeToRemove cosmosMath.Int,
) error {
	// CHECKS
	if stakeToRemove.IsZero() {
		return nil
	}

	// stakeSumFromDelegator >= stake
	stakeSumFromDelegator, err := k.GetStakeFromDelegatorInTopic(ctx, topicId, delegator)
	if err != nil {
		return err
	}
	if stakeToRemove.GT(stakeSumFromDelegator) {
		return types.ErrIntegerUnderflowStakeFromDelegator
	}
	stakeFromDelegatorNew := stakeSumFromDelegator.Sub(stakeToRemove)

	// delegatedStakePlacement >= stake
	delegatedStakePlacement, err := k.GetDelegateStakePlacement(ctx, topicId, delegator, reputer)
	if err != nil {
		return err
	}
	unStakeDec, err := alloraMath.NewDecFromSdkInt(stakeToRemove)
	if err != nil {
		return err
	}
	if delegatedStakePlacement.Amount.Lt(unStakeDec) {
		return types.ErrIntegerUnderflowDelegateStakePlacement
	}

	// Get share for this topicId and reputer
	share, err := k.GetDelegateRewardPerShare(ctx, topicId, reputer)
	if err != nil {
		return err
	}

	// Calculate pending reward and send to delegator
	pendingReward, err := delegatedStakePlacement.Amount.Mul(share)
	if err != nil {
		return err
	}
	pendingReward, err = pendingReward.Sub(delegatedStakePlacement.RewardDebt)
	if err != nil {
		return err
	}
	if pendingReward.Gt(alloraMath.NewDecFromInt64(0)) {
		err = k.SendCoinsFromModuleToAccount(
			ctx,
			types.AlloraPendingRewardForDelegatorAccountName,
			delegator,
			sdk.NewCoins(sdk.NewCoin(params.DefaultBondDenom, pendingReward.SdkIntTrim())),  // <===== Audit
		)
		if err != nil {
			return errorsmod.Wrapf(err, "Sending pending reward to delegator failed")
		}
	}

	newAmount, err := delegatedStakePlacement.Amount.Sub(unStakeDec)
	if err != nil {
		return err
	}
	newRewardDebt, err := newAmount.Mul(share)  // <===== Audit
	if err != nil {
		return err
	}
	stakePlacementNew := types.DelegatorInfo{
		Amount:     newAmount,
		RewardDebt: newRewardDebt, // <===== Audit
	}
        // ...
}
```

[](https://github.com/sherlock-audit/2024-06-allora/blob/main/allora-chain/x/emissions/keeper/keeper.go#L749-L854)
```golang
func (k *Keeper) AddDelegateStake(
	ctx context.Context,
	topicId TopicId,
	delegator ActorId,
	reputer ActorId,
	stakeToAdd cosmosMath.Int,
) error {
	// CHECKS
	if stakeToAdd.IsZero() {
		return errorsmod.Wrapf(types.ErrInvalidValue, "delegator stake to add must be greater than zero")
	}

	// GET CURRENT VALUES
	totalStake, err := k.GetTotalStake(ctx)
	if err != nil {
		return err
	}
	totalStakeNew := totalStake.Add(stakeToAdd)
	topicStake, err := k.GetTopicStake(ctx, topicId)
	if err != nil {
		return err
	}
	topicStakeNew := topicStake.Add(stakeToAdd)
	stakeReputerAuthority, err := k.GetStakeReputerAuthority(ctx, topicId, reputer)
	if err != nil {
		return err
	}
	stakeReputerAuthorityNew := stakeReputerAuthority.Add(stakeToAdd)
	stakeSumFromDelegator, err := k.GetStakeFromDelegatorInTopic(ctx, topicId, delegator)
	if err != nil {
		return err
	}
	stakeSumFromDelegatorNew := stakeSumFromDelegator.Add(stakeToAdd)
	delegateStakePlacement, err := k.GetDelegateStakePlacement(ctx, topicId, delegator, reputer)
	if err != nil {
		return err
	}
	share, err := k.GetDelegateRewardPerShare(ctx, topicId, reputer)
	if err != nil {
		return err
	}
	if delegateStakePlacement.Amount.Gt(alloraMath.NewDecFromInt64(0)) {
		// Calculate pending reward and send to delegator
		pendingReward, err := delegateStakePlacement.Amount.Mul(share)
		if err != nil {
			return err
		}
		pendingReward, err = pendingReward.Sub(delegateStakePlacement.RewardDebt)
		if err != nil {
			return err
		}
		if pendingReward.Gt(alloraMath.NewDecFromInt64(0)) {
			err = k.SendCoinsFromModuleToAccount(
				ctx,
				types.AlloraPendingRewardForDelegatorAccountName,
				delegator,
				sdk.NewCoins(sdk.NewCoin(params.DefaultBondDenom, pendingReward.SdkIntTrim())),  // <===== Audit
			)
			if err != nil {
				return err
			}
		}
	}
	stakeToAddDec, err := alloraMath.NewDecFromSdkInt(stakeToAdd)
	if err != nil {
		return err
	}
	newAmount, err := delegateStakePlacement.Amount.Add(stakeToAddDec)
	if err != nil {
		return err
	}
	newDebt, err := newAmount.Mul(share)  // <===== Audit
	if err != nil {
		return err
	}
	stakePlacementNew := types.DelegatorInfo{
		Amount:     newAmount,
		RewardDebt: newDebt,  // <===== Audit
	}
	// ...
}
```

## Tool used
Manual Review

## Recommendation
* Check if the trimmed amount (instead of the untrimmed) is greater than zero.
* Only increase the reward debt by the sent trimmed amount.
