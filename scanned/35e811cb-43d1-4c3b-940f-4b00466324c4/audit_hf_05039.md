# [H] GenerateForecastScores aci- dentally updates inferences scores

## Summary
Severity: High
Reporter: 0x3b
Contest weight: 0.3813
Dataset id: 23043
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GenerateForecastScores, used to update forecasts, will update a worker's inference scores with the forecast values. This can have a massive impact as it messes up both scores — by not updating the forecast and setting the inference to a new, different value.
GenerateRewardsDistributionByTopicParticipant is used to update and calculate each party's rewards. Inside it, it makes a plethora of calls, one of which is GenerateForecastScores, used to update forecast score values.
The issue we face is that in GenerateForecastScores, if there is only one forecaster, it will insert its inference score in the place of the forecast using InsertWorkerInferenceScore.
s/module/rewards/scores.go#L195
```go
func GenerateForecastScores(
ctx sdk.Context,
keeper keeper.Keeper,
topicId uint64,
block int64,
networkLosses types.ValueBundle,
) ([]types.Score, error) {
    var newScores []types.Score
    if len(networkLosses.ForecasterValues) == 1 {
        newScore := types.Score{
            TopicId:      topicId,
            BlockHeight:  block,
            Address:      networkLosses.InfererValues[0].Worker,
            Score:        alloraMath.ZeroDec(),
        }
        err := keeper.InsertWorkerInferenceScore(ctx, topicId, block, newScore)
        ...
    }
}
```
This can pose a major issue as GetWorkersRewardFractions calculates worker rewards based on their last few scores. Inserting a wrong score messes up their rewards.
Having only one forecaster may be considered rare, however, that is not the case, as these forecasts are per topic per block. This means that each topic (there can be a lot of them) can have different forecasts each new block (block time ~5 seconds). Taking into account that the chain will operate 24/7 this can occurrence can take place quite often.
Internal accounting of worker scores and rewards (they are calculated based on score) are messed up. Depending on the values, workers will receive more or less rewards than they should.
```go
func GenerateForecastScores(
ctx sdk.Context,
keeper keeper.Keeper,
topicId uint64,
block int64,
networkLosses types.ValueBundle,
) ([]types.Score, error) {
    var newScores []types.Score
    if len(networkLosses.ForecasterValues) == 1 {
        newScore := types.Score{
            TopicId:      topicId,
            BlockHeight:  block,
            Address:      networkLosses.InfererValues[0].Worker,
            Score:        alloraMath.ZeroDec(),
        }
        err := keeper.InsertWorkerInferenceScore(ctx, topicId, block, newScore)
        ...
    }
}
```

## Recommendation
Change the insertion to InsertWorkerForecastScore:
```diff
- err := keeper.InsertWorkerInferenceScore(ctx, topicId, block, newScore)
+ err := keeper.InsertWorkerForecastScore(ctx, topicId, block, newScore)
```
