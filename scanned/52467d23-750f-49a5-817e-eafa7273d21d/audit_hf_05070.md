# [M] SafeApplyFuncOnAllActiveEp-

## Summary
Severity: Medium
Contest weight: 0.3655
Dataset id: 23081
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SafeApplyFuncOnAllActiveEpochEndingTopics processes more pages than the desired processing is done. This means that two more pages will be processed. For example, if the max topic pages is 100:
• The current iteration needs to be at least 101 to break.
• Since the current iteration is only incremented after the check and processing are done, two additional pages may get processed.

Processing topic rewards for more active topics than intended.
```go
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

## Proof of Concept
```go
func (s *RewardsTestSuite) TestSafeApplyFuncOnAllActiveEpochEndingTopics() {
    ctx := s.ctx
    k := s.emissionsKeeper
    for i := 0; i < 200; i++ {
        topic := types.Topic{Id: uint64(i), EpochLength: math.MaxInt64}
        k.SetTopic(ctx, topic.Id, topic)
        k.ActivateTopic(ctx, topic.Id)
    }
    limit := uint64(10)
    countProcessed := 0
    fn := func(ctx sdk.Context, topic *types.Topic) error {
        countProcessed++
        return nil
    }
    rewards.SafeApplyFuncOnAllActiveEpochEndingTopics(ctx, k, ctx.BlockHeight(), fn, limit, limit)
    s.Require().Equal(countProcessed, 100)
}
=== RUN   TestModuleTestSuite/TestSafeApplyFuncOnAllActiveEpochEndingTopics
topic_rewards_test.go:31:
Error Trace:
    allora-chain/x/emissions/module/rewards/topic_rewards_test.go:31
Error:
    Not equal:
        expected: 120
        actual  : 100
Test:
    TestModuleTestSuite/TestSafeApplyFuncOnAllActiveEpochEndingTopics
```

## Recommendation
Check if the maxTopicPages is reached at the beginning of the loop
```diff
diff --git a/allora-chain/x/emissions/module/rewards/topic_rewards.go b/allora-chain/x/emissions/module/rewards/topic_rewards.go
index fa67db0..7a75612 100644
--- a/allora-chain/x/emissions/module/rewards/topic_rewards.go
+++ b/allora-chain/x/emissions/module/rewards/topic_rewards.go
@@ -61,6 +61,10 @@ func SafeApplyFuncOnAllActiveEpochEndingTopics(
    topicPageKey := make([]byte, 0)
    i := uint64(0)
    for {
+       if i >= maxTopicPages {
+           break
+       }
+
        topicPageRequest := &types.SimpleCursorPaginationRequest{Limit: topicPageLimit, Key: topicPageKey}
        topicsActive, err := k.GetIdsOfActiveTopicsPaginatedStream(ctx, topicPageRequest)
        if err != nil {
@@ -86,7 +90,7 @@ func SafeApplyFuncOnAllActiveEpochEndingTopics(
        }
-       if topicsActive == nil || i > maxTopicPages {
+       if topicsActive == nil {
            break
        }
```
