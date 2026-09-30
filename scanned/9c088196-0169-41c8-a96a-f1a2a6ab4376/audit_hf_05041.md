# [H] emissions/keeper/

## Summary
Severity: High
Contest weight: 0.3714
Dataset id: 23045
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GetIdsOfActiveTopics may always return empty array, causing topicweights to not be updated.
IterateRaw is used in the GetIdsOfActiveTopics function to iterate over the map
startKey := make([]byte, binary.MaxVarintLen64)
binary.BigEndian.PutUint64(startKey, start)
nextKey := make([]byte, binary.MaxVarintLen64)
binary.BigEndian.PutUint64(nextKey, start+limit)
rng, err := k.activeTopics.IterateRaw(ctx, startKey, nextKey, collections.OrderAscending)
if err != nil {
return nil, nil, err
}
activeTopics, err := rng.Keys()
if err != nil {
return nil, nil, err
}
startKey starts from 0: topicPageKey := make([]byte, 0)
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
if err != nil {
Logger(ctx).Warn(fmt.Sprintf("Error getting ids of active topics: %s", err.Error()))
continue
}
}
The problem is that if the element in activeTopics does not start at 0, IterateRaw will return less data than the number of pageLimit. Suppose the elements in activeTopics are 20 to 100, startKey is 0, pageLimit is 10, IterateRaw returns a null value.
If null is returned, GetIdsOfActiveTopics returns nextKey starting from 0, SafeApplyFuncOnAllActiveEpochEndingTopics function of topicPageKey has not updated, so has been unable to get to the value.
// If there are no topics, we return the nil for next key
if activeTopics == nil {
nextKey = make([]byte, 0)
}
NextKey: nextKey,
}, nil
The following test code demonstrates a case where GetIdsOfActiveTopics can't get the value:
func (s *KeeperTestSuite) TestGetActiveTopics1() {
ctx := s.ctx
keeper := s.emissionsKeeper
for i := 20; i < 100; i++ {
topic1 := types.Topic{Id: uint64(i)}
_ = keeper.SetTopic(ctx, topic1.Id, topic1)
_ = keeper.ActivateTopic(ctx, topic1.Id)
}
topicPageKey := make([]byte, 0)
pagination := &types.SimpleCursorPaginationRequest{
Key: topicPageKey,
Limit: 10,
}
fmt.Println(len(activeTopics))
}
Put the test code into the test file: allora-chain/x/emissions/keeper/keeper_test.go
cd allora-chain/x/emissions/keeper/ go test -v -run TestKeeperTestSuite/TestGetActiveTopics1
Print input as follows::
=== RUN TestKeeperTestSuite
=== RUN TestKeeperTestSuite/TestGetActiveTopics1
[]
--- PASS: TestKeeperTestSuite (0.00s)
--- PASS: TestKeeperTestSuite/TestGetActiveTopics1 (0.00s)
PASS
Let's look at the call flow: emissions/module/acbi/EndEndBlocker -> rewards.GetAndUpdateActiveTopicWeights -> SafeApplyFuncOnAllActiveEpochEndingTopics -> k.GetIdsOfActiveTopics
If GetIdsOfActiveTopics always returns empty [], topicweights will not be updated and topicRewards will not be processed.
After a topic is created, not all topics will be activated. If an attacker(or just normal users who want to keep some topics) creates pageLimit number of topics while the network is online, and these topics never enter Activate state, it will happen that the GetIdsOfActiveTopics function will always return a null value.
GetIdsOfActiveTopics always return empty array, causing topicweights to not be updated.

## Recommendation
Use other paging methods
