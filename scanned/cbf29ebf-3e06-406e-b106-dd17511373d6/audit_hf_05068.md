# [M] The issue of SLOW ABCI METH-

## Summary
Severity: Medium
Contest weight: 0.2466
Dataset id: 23079
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SLOW ABCI METHODS - SafeApplyFuncOnAllActiveEpochEndingTopics is called by the GetAndUpdateActiveTopicWeights function, which is called in the EndBlocker() function in abci.go. Taking the SafeApplyFuncOnAllActiveEpochEndingTopics function as an example:
```go
// Apply a function on all active topics that also have an epoch ending at this block
// Active topics have more than a globally-set minimum weight, a function of revenue and stake
// "Safe" because bounded by max number of pages and apply running, online operations.
func SafeApplyFuncOnAllActiveEpochEndingTopics(
    ctx sdk.Context,
    k keeper.Keeper,
    block BlockHeight,
    fn func(sdkCtx sdk.Context, topic *types.Topic) error,
    topicPageLimit uint64,
    maxTopicPages uint64,
) error {
    topicPageKey := make([]byte, 0)
    i := uint64(0)
    for {
        topicPageRequest := &types.SimpleCursorPaginationRequest{Limit: topicPageLimit, Key: topicPageKey}
        topicsActive, err := k.GetIdsOfActiveTopicsPaginatedStream(ctx, topicPageRequest)
        if err != nil {
            Logger(ctx).Warn(fmt.Sprintf("Error getting ids of active topics: %s", err.Error()))
            continue
        }
        for _, topicId := range topicsActive {
            topic, err := k.GetTopic(ctx, topicId)
            if err != nil {
                Logger(ctx).Warn(fmt.Sprintf("Error getting topic: %s", err.Error()))
                continue
            }
            if k.CheckCadence(block, topic) {
                // All checks passed => Apply function on the topic
                err = fn(ctx, &topic)
                if err != nil {
                    Logger(ctx).Warn(fmt.Sprintf("Error applying function on topic: %s", err.Error()))
                    continue
                }
            }
        }
        if topicsActive == nil || i > maxTopicPages {
            break
        }
        i++
    }
    return nil
}
```
In the SafeApplyFuncOnAllActiveEpochEndingTopics function, although topicPageLimit and maxTopicPages have been added to control the number of iterations, this introduces new issues. Below are two scenarios:
1. topicPageLimit * maxTopicPages < totalTopicNumbers: In this case, because the number of topics iterated over is less than the total number of topics, some topics will never be processed, causing their state to be out of date.
2. topicPageLimit * maxTopicPages >= totalTopicNumbers: In this case, all topics can be processed, but this introduces a high computational cost, such as multiple nested loops, which could slow down the execution of nodes and block production. In the worst case, this could lead to a halt of the chain. The topic data could become out of date, or multiple nested loops could slow down the execution of nodes and block production, potentially leading to a halt of the chain in the worst case.

## Recommendation
their computational complexity and ensuring they will scale correctly with the application's usage growth.
