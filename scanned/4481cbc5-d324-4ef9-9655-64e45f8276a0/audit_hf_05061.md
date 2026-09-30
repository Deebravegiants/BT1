# [M] RemoveDelegateStake silently

## Summary
Severity: Medium
Contest weight: 0.1543
Dataset id: 23071
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RemoveDelegateStake silently handles the error when checking for existing removals
RemoveDelegateStake silently handles the error when checking for existing removals while RemoveStake blocks further processing and returns the error.
Delegate stake removal will be created even if an error happens when checking for existing removals.
RemoveDelegateStake
func (ms msgServer) RemoveDelegateStake(ctx context.Context, msg *types.MsgRemoveDelegateStake) (*types.MsgRemoveDelegateStakeResponse, error) {
sdkCtx := sdk.UnwrapSDKContext(ctx)
removal, found, err :=
ms.k.GetDelegateStakeRemovalForDelegatorReputerAndTopicId(
sdkCtx, msg.Sender, msg.Reputer, msg.TopicId,
)
if err != nil {
errorsmod.Wrap(err, "error during finding delegate stake removal") //
}
}
RemoveStake
func (ms msgServer) RemoveStake(ctx context.Context, msg *types.MsgRemoveStake) (*types.MsgRemoveStakeResponse, error) {
sdkCtx := sdk.UnwrapSDKContext(ctx)
removal, found, err := ms.k.GetStakeRemovalForReputerAndTopicId(sdkCtx,
msg.Sender, msg.TopicId)
if err != nil {
return nil, errorsmod.Wrap(err, "error while searching previous stake")
}
}

## Recommendation
Return the error from RemoveDelegateStake
