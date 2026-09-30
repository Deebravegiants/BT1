# [H] forecast-implied inferences can

## Summary
Severity: High
Contest weight: 0.2052
Dataset id: 23042
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
forecast-implied inferences can be set to any value due to ForecastElements is not filtered by duplicate.
The function InsertBulkWorkerPayload doesn't have any authentication. There is no validation for duplicates inside the input variable workerDataBundle.InferenceForecastsBundle.Forecast.ForecastElements
for _, el := range forecast.ForecastElements {
    if _, ok := acceptedInferersOfBatch[el.Inferer]; ok {
        acceptedForecastElements = append(acceptedForecastElements, el)
    }
}
// Discard if empty
if len(acceptedForecastElements) == 0 {
    continue
}
msg_server_worker_payload.go#L164 .ForecastElements is being used inside CalcForecastImpliedInferences to calculate forecast-implied inference value.
forecastValue can be set to any value due to duplication

## Recommendation
Filter out duplicates inside workerDataBundle.InferenceForecastsBundle.Forecast.ForecastElements inside verifyAndInsertForecastsFromTopForecasters before saving via ms.k.InsertForecasts(
