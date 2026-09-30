# [M] The SelectTopNWorkerNonces

## Summary
Severity: Medium
Contest weight: 0.2456
Dataset id: 23066
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SelectTopNWorkerNonces function lacks a sorting algorithm internally and only selects N workers from the array.
func SelectTopNWorkerNonces(workerNonces emissions.Nonces, N int) []*emissions.Nonce {
if len(workerNonces.Nonces) <= N {
return workerNonces.Nonces
}
return workerNonces.Nonces[:N]
}
We can see that the function lacks a sorting algorithm and only selects N workers from the array. The SelectTopNWorkerNonces function is used in the requestTopicWorkers function.
func (th *TopicsHandler) requestTopicWorkers(ctx sdk.Context, topic emissionstypes.Topic) {
Logger(ctx).Debug(fmt.Sprintf("Triggering inference generation for topic: %v metadata: %s default arg: %s. \n",
topic.Id, topic.Metadata, topic.DefaultArg))
workerNonces, err := th.emissionsKeeper.GetUnfulfilledWorkerNonces(ctx,
topic.Id)
if err != nil {
Logger(ctx).Error("Error getting worker nonces: " + err.Error())
return
}
// Filter workerNonces to only include those that are within the epoch length
// This is to avoid requesting inferences for epochs that have already ended
workerNonces = synth.FilterNoncesWithinEpochLength(workerNonces,
ctx.BlockHeight(), topic.EpochLength)
maxRetriesToFulfilNoncesWorker :=
emissionstypes.DefaultParams().MaxRetriesToFulfilNoncesWorker
emissionsParams, err := th.emissionsKeeper.GetParams(ctx)
if err != nil {
Logger(ctx).Warn(fmt.Sprintf("Error getting max retries to fulfil nonces for worker requests (using default), err: %s", err.Error()))
} else {
maxRetriesToFulfilNoncesWorker =
emissionsParams.MaxRetriesToFulfilNoncesWorker
}
sortedWorkerNonces := synth.SelectTopNWorkerNonces(workerNonces,
int(maxRetriesToFulfilNoncesWorker))
Logger(ctx).Debug(fmt.Sprintf("Iterating Top N Worker Nonces: %d",
len(sortedWorkerNonces)))
// iterate over all the worker nonces to find if this is unfulfilled
for _, nonce := range sortedWorkerNonces {
nonceCopy := nonce
Logger(ctx).Debug(fmt.Sprintf("Current Worker block height has been found unfulfilled, requesting inferences %v", nonceCopy))
go generateInferencesRequest(ctx, topic.InferenceLogic,
topic.InferenceMethod, topic.DefaultArg, topic.Id, topic.AllowNegative,
*nonceCopy)
}
}
It can be seen that workerNonces is unsorted data, and after being processed by synth.SelectTopNWorkerNonces, it only selects N workers from the array rather than selecting the latest N workers based on the Nonce.
It does not select the top N latest worker nonces as intended. Moreover, selecting workers not within the top might result in choosing workers that are already offline or not able to return the desired data correctly.

## Recommendation
Add the SortByBlockHeight function within the SelectTopNWorkerNonces function.
