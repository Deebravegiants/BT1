# [H] SetDelegateStakePlacement er-

## Summary
Severity: High
Contest weight: 0.3286
Dataset id: 23067
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SetDelegateStakePlacement error is not handled in RewardDelegateStake.
If SetDelegateStakePlacement fails in RewardDelegateStake, the RewardDebt will not be saved and it would allow a delegate staker to claim the same rewards more than once.
Rewards being distributed more than once can lead to insolvency (.i.e : others delegate stakers not being able to claim their rewards) and the drainage of the AlloraPendingReward module account.
RewardDelegateStake
func (ms msgServer) RewardDelegateStake(ctx context.Context, msg *types.MsgRewardDelegateStake) (*types.MsgRewardDelegateStakeResponse, error) {
// Check the target reputer exists and is registered
isRegistered, err := ms.k.IsReputerRegisteredInTopic(ctx, msg.TopicId,
msg.Reputer)
if err != nil {
return nil, err
}
if !isRegistered {
return nil, types.ErrAddressIsNotRegisteredInThisTopic
}
delegateInfo, err := ms.k.GetDelegateStakePlacement(ctx, msg.TopicId,
msg.Sender, msg.Reputer)
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
if pendingReward.Gt(alloraMath.NewDecFromInt64(0)) {
coins := sdk.NewCoins(sdk.NewCoin(params.DefaultBondDenom,
pendingReward.SdkIntTrim()))
err = ms.k.SendCoinsFromModuleToAccount(ctx,
types.AlloraPendingRewardForDelegatorAccountName, msg.Sender, coins)
if err != nil {
return nil, err
}
delegateInfo.RewardDebt, err = delegateInfo.Amount.Mul(share)
if err != nil {
return nil, err
}
ms.k.SetDelegateStakePlacement(ctx, msg.TopicId, msg.Sender, msg.Reputer,
&delegateInfo)
}
}

## Recommendation
Handle the SetDelegateStakePlacement error.
