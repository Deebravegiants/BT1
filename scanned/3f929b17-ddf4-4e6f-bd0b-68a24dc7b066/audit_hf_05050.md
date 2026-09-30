# [H] Not appropriate Inferences will

## Summary
Severity: High
Contest weight: 0.3205
Dataset id: 23054
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Not appropriate Inferences will be used when calculating the forecast due to not saving filtered results
Current variable acceptedInferersOfBatch doesn't do anything due to acceptedForecastElements is not being saved. It should filter out accepted Inferers according to the forecast
func verifyAndInsertForecastsFromTopForecasters(
ctx context.Context,
ms msgServer,
topicId uint64,
nonce types.Nonce,
workerDataBundle []*types.WorkerDataBundle,
// Inferers in the current batch, assumed to have passed
VerifyAndInsertInferencesFromTopInferers() filters
acceptedInferersOfBatch map[string]bool,
maxTopWorkersToReward uint64,
) error {
// Examine forecast elements to verify that they're for inferers in the current set.
// We assume that set of inferers has been verified above.
// We keep what we can, ignoring the forecaster and their contribution (forecast) entirely
// if they're left with no valid forecast elements.
acceptedForecastElements := make([]*types.ForecastElement, 0)
for _, el := range forecast.ForecastElements {
if _, ok := acceptedInferersOfBatch[el.Inferer]; ok {
acceptedForecastElements = append(acceptedForecastElements, el)
}
}
...
keeper/msgserver/msg_server_worker_payload.go#L163
Not appropriate Inferences will be used when calculating the forecast

## Recommendation
It should look like this
acceptedForecastElements := make([]*types.ForecastElement, 0)
for _, el := range forecast.ForecastElements {
if _, ok := acceptedInferersOfBatch[el.Inferer]; ok {
acceptedForecastElements = append(acceptedForecastElements, el)
}
}
// Discard if empty
if len(acceptedForecastElements) == 0 {
continue
}
+
forecast.ForecastElements = acceptedForecastElements;
/// Filtering done now, now write what we must for inclusion
// Get the latest score for each forecaster => only take top few by score descending
latestScore, err := ms.k.GetLatestForecasterScore(ctx, topicId, forecast.Forecaster)
if err != nil {
continue
}
latestForecasterScores[forecast.Forecaster] = latestScore
forecastsByForecaster[forecast.Forecaster] = forecast
}
