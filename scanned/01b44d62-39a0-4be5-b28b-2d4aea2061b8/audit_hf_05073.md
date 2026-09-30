# [M] Lack of error handling when

## Summary
Severity: Medium
Contest weight: 0.2427
Dataset id: 23085
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Lack of error handling when making blockless api call. Error handling when making blockless api call is missing. In topics_handler.go, we are calling PrepareProposalHandler
```go
func (th *TopicsHandler) PrepareProposalHandler() sdk.PrepareProposalHandler {
    return func(ctx sdk.Context, req *abci.RequestPrepareProposal) *abci.ResponsePrepareProposal {
        Logger(ctx).Debug("\n ---------------- TopicsHandler ------------------- \n")
        churnableTopics, err := th.emissionsKeeper.GetChurnableTopics(ctx)
        if err != nil {
            Logger(ctx).Error("Error getting max number of topics per block: " + err.Error())
            return nil, err
        }
        var wg sync.WaitGroup
        // Loop over and run epochs on topics whose inferences are demanded enough to be served
        // Within each loop, execute the inference and weight cadence checks and trigger the inference and weight generation
        for _, churnableTopicId := range churnableTopics {
            wg.Add(1)
            go func(topicId TopicId) {
                defer wg.Done()
                topic, err := th.emissionsKeeper.GetTopic(ctx, topicId)
                if err != nil {
                    Logger(ctx).Error("Error getting topic: " + err.Error())
                }
                th.requestTopicWorkers(ctx, topic)
                th.requestTopicReputers(ctx, topic)
            }(churnableTopicId)
        }
        wg.Wait()
        // Return the transactions as they came
    }
}
```
These two functions requestTopicWorkers and requestTopicReputers trigger blockless api calls. For example, the requestTopicReputers => go generateInferencesRequest => makeApiCall
```go
err = makeApiCall(payloadStr)
if err != nil {
    Logger(ctx).Warn(fmt.Sprintf("Error making API call: %s", err.Error()))
}
```
The api call can fail for many reasons, and if it fails, the code only log the error and does not return the error and bubble the error up for error handling. Then it means that the loss and inference request is never sent out and updated, the PrepareProposalHandler will still silently assume the call always success and go through, this leads to loss and inference data severely out of scope.

## Recommendation
handle the error from api call
