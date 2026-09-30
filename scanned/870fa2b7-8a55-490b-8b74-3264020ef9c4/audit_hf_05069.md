# [M] DripTopicFeeRevenue drips the

## Summary
Severity: Medium
Contest weight: 0.2456
Dataset id: 23080
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DripTopicFeeRevenue drips the topicFeeRevenue storage value instead of the value provided by the calculations inside GetCurrentTopicWeight. This can lead to different drip amounts than the ones calculated. When GetAndUpdateActiveTopicWeights calls DripTopicFeeRevenue, it doesn't take the previously calculated topicFeeRevenue from GetCurrentTopicWeight.
```go
weight, topicFeeRevenue, err := k.GetCurrentTopicWeight(
    ctx,
    topic.Id,
    topic.EpochLength,
    moduleParams.TopicRewardAlpha,
    moduleParams.TopicRewardStakeImportance,
    moduleParams.TopicRewardFeeRevenueImportance,
    cosmosMath.ZeroInt(),
)
```
Instead, DripTopicFeeRevenue extracts the revenue from storage and drips that.
```go
func (k *Keeper) DripTopicFeeRevenue(ctx context.Context, topicId TopicId, block BlockHeight) error {
    topicFeeRevenue, err := k.GetTopicFeeRevenue(ctx, topicId)
    if err != nil {
        return err
    }
```
However, if GetCurrentTopicWeight calculates a larger revenue because it includes a bonus, that bonus will never be dripped. The bonus is calculated here inside GetCurrentTopicWeight:
```go
newFeeRevenue := additionalRevenue.Add(topicFeeRevenue)
feeRevenue, err := alloraMath.NewDecFromSdkInt(newFeeRevenue)
if err != nil {
    return alloraMath.Dec{}, cosmosMath.Int{}, errors.Wrapf(err, "failed to convert topic fee revenue to dec")
}
```
DripTopicFeeRevenue may drip less than what is reported in totalRevenue.
```go
weight, topicFeeRevenue, err := k.GetCurrentTopicWeight(
    ctx,
    topic.Id,
    topic.EpochLength,
    moduleParams.TopicRewardAlpha,
    moduleParams.TopicRewardStakeImportance,
    moduleParams.TopicRewardFeeRevenueImportance,
    cosmosMath.ZeroInt(),
)
if err != nil {
    return errors.Wrapf(err, "failed to get current topic weight")
}
err = k.SetPreviousTopicWeight(ctx, topic.Id, weight)
if err != nil {
    return errors.Wrapf(err, "failed to set previous topic weight")
}
err = k.DripTopicFeeRevenue(ctx, topic.Id, block)
if err != nil {
    return errors.Wrapf(err, "failed to reset topic fee revenue")
}
```

## Recommendation
Make DripTopicFeeRevenue take a parameter topicFeeRevenue and drip that amount.
