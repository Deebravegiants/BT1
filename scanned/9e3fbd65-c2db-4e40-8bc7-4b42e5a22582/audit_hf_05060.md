# [M] Some Iterators are not closed in

## Summary
Severity: Medium
Contest weight: 0.2448
Dataset id: 23070
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Some Iterators are not closed in emissions module Keeper
GetStakeRemovalsForBlock, GetDelegateStakeRemovalsForBlock, GetInferenceScoresUntilBlock, GetForecastScoresUntilBlock do not Close the Iterator they create.
For reference:
https://docs.cosmos.network/main/build/packages/collections#iterateaccounts
Unless Keys, Values, KeyValues or Walk are used, a collection Iterator must be explicitly closed and here they aren't.
GetStakeRemovalsForBlock
func (k *Keeper) GetStakeRemovalsForBlock(
ctx context.Context,
blockHeight BlockHeight,
) ([]types.StakeRemovalInfo, error) {
ret := make([]types.StakeRemovalInfo, 0)
iter, err := k.stakeRemovalsByBlock.Iterate(ctx, collections.Range[BlockHeight](blockHeight))
if err != nil {
return ret, err
}
for ; iter.Valid(); iter.Next() {
val, err := iter.Value()
if err != nil {
return ret, err
}
ret = append(ret, val)
}
return ret, nil
}
GetDelegateStakeRemovalsForBlock
func (k *Keeper) GetDelegateStakeRemovalsForBlock(
ctx context.Context,
blockHeight BlockHeight,
) ([]types.DelegateStakeRemovalInfo, error) {
ret := make([]types.DelegateStakeRemovalInfo, 0)
rng := collections.
Range[BlockHeight](blockHeight)
iter, err := k.delegateStakeRemovalsByBlock.Iterate(ctx, rng)
if err != nil {
return ret, err
}
for ; iter.Valid(); iter.Next() {
val, err := iter.Value()
if err != nil {
return ret, err
}
ret = append(ret, val)
}
return ret, nil
}
GetInferenceScoresUntilBlock
func (k *Keeper) GetInferenceScoresUntilBlock(ctx context.Context, topicId TopicId,
blockHeight BlockHeight) ([]*types.Score, error) {
rng := collections.
Prefix(topicId).
EndInclusive(blockHeight).
Descending()
scores := make([]*types.Score, 0)
iter, err := k.infererScoresByBlock.Iterate(ctx, rng)
if err != nil {
return nil, err
}
// Get max number of time steps that should be retrieved
moduleParams, err := k.GetParams(ctx)
if err != nil {
return nil, err
}
maxNumTimeSteps := moduleParams.MaxSamplesToScaleScores
count := 0
for ; iter.Valid() && count < int(maxNumTimeSteps); iter.Next() {
existingScores, err := iter.KeyValue()
if err != nil {
return nil, err
}
for _, score := range existingScores.Value.Scores {
scores = append(scores, score)
count++
}
}
return scores, nil
}
GetForecastScoresUntilBlock
func (k *Keeper) GetForecastScoresUntilBlock(ctx context.Context, topicId TopicId,
blockHeight BlockHeight) ([]*types.Score, error) {
rng := collections.
Prefix(topicId).
EndInclusive(blockHeight).
Descending()
scores := make([]*types.Score, 0)
iter, err := k.forecasterScoresByBlock.Iterate(ctx, rng)
if err != nil {
return nil, err
}
// Get max number of time steps that should be retrieved
moduleParams, err := k.GetParams(ctx)
if err != nil {
return nil, err
}
maxNumTimeSteps := moduleParams.MaxSamplesToScaleScores
count := 0
for ; iter.Valid() && count < int(maxNumTimeSteps); iter.Next() {
existingScores, err := iter.KeyValue()
if err != nil {
return nil, err
}
for _, score := range existingScores.Value.Scores {
scores = append(scores, score)
count++
}
}
return scores, nil
}

## Recommendation
Explicitly Close the Iterators with "defer iter.Close()"
