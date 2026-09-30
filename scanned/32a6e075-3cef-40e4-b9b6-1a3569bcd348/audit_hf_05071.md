# [M] GetForecastScoresUntilBlock

## Summary
Severity: Medium
Contest weight: 0.2462
Dataset id: 23082
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A for loop inside GetForecastScoresUntilBlock can accidentally pick different sized sample for participants scores, which will lead to different rewards. The for loop inside GetForecastScoresUntilBlock that extracts score samples has count<int(maxNumTimeSteps) where it would prevent it from appending more score samples than the maxNumTimeSteps.
```go
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
```
However as we can see score is iterated inside the inner for loop and that one doesn't stop even if we surpass maxNumTimeSteps. This would cause a discrepancy between different topics and workers, as GetForecastScoresUntilBlock is used inside GenerateRewardsDistributionByTopicParticipant (GetForecastingTaskRewardFractions -> GetWorkersRewardFractions) to generate the scores and from them the rewards each worker should have.
```go
latestScoresFromLastestTimeSteps, err := k.GetInferenceScoresUntilBlock(ctx, topicId, blockHeight)
if err != nil {
    return []string{}, []alloraMath.Dec{}, errors.Wrapf(err, "failed to get worker inference scores from the latest time steps")
}
var workerLastScoresDec []alloraMath.Dec
for _, score := range latestScoresFromLastestTimeSteps {
    workerLastScoresDec = append(workerLastScoresDec, score.Score)
}
scores = append(scores, workerLastScoresDec)
...
rewardFractions, err := GetScoreFractions(latestWorkerScores, flatten(scores), pReward, cReward, moduleParams.Epsilon)
if err != nil {
    return []string{}, []alloraMath.Dec{}, errors.Wrapf(err, "failed to get score fractions")
}
return workers, rewardFractions, nil
```
Having different number of score samples (some above the max) will yield different results when it comes to reward calculation. Workers will calculate different reward fractions (done inside GetWorkersRewardFractions) even if the scores are the same, as the for loop may pick max scores for one topic and above the max for another.
```go
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
```

## Recommendation
Have the cap also inside the inner for loop to prevent picking more scores than the max limit.
