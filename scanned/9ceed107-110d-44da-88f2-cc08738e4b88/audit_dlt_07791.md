# [?] Fix Deadlock in StreamChainHead (#12250)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2023-04-07
Source: https://github.com/OffchainLabs/prysm/commit/37182168e313f652ba40b4d64cc53f325b944895
Type: security-commit

## Details
Fix Deadlock in StreamChainHead (#12250)

* fix it possibly

* buffer it more

* fix test

## Patch
### beacon-chain/rpc/prysm/v1alpha1/beacon/blocks.go
```diff
@@ -346,12 +346,19 @@ func (bs *Server) StreamBlocks(req *ethpb.StreamBlocksRequest, stream ethpb.Beac
 // StreamChainHead to clients every single time the head block and state of the chain change.
 // DEPRECATED: This endpoint is superseded by the /eth/v1/events Beacon API endpoint
 func (bs *Server) StreamChainHead(_ *emptypb.Empty, stream ethpb.BeaconChain_StreamChainHeadServer) error {
-	stateChannel := make(chan *feed.Event, 1)
+	stateChannel := make(chan *feed.Event, 4)
 	stateSub := bs.StateNotifier.StateFeed().Subscribe(stateChannel)
 	defer stateSub.Unsubscribe()
 	for {
 		select {
 		case stateEvent := <-stateChannel:
+			// In the event our node is in sync mode
+			// we do not send the chainhead to the caller
+			// due to the possibility of deadlocks when retrieving
+			// all the chain related data.
+			if bs.SyncChecker.Syncing() {
+				continue
+			}
 			if stateEvent.Type == statefeed.BlockProcessed {
 				res, err := bs.chainHeadRetrieval(stream.Context())
 				if err != nil {
```

### beacon-chain/rpc/prysm/v1alpha1/beacon/blocks_test.go
```diff
@@ -13,6 +13,7 @@ import (
 	statefeed "github.com/prysmaticlabs/prysm/v4/beacon-chain/core/feed/state"
 	dbTest "github.com/prysmaticlabs/prysm/v4/beacon-chain/db/testing"
 	state_native "github.com/prysmaticlabs/prysm/v4/beacon-chain/state/state-native"
+	mockSync "github.com/prysmaticlabs/prysm/v4/beacon-chain/sync/initial-sync/testing"
 	"github.com/prysmaticlabs/prysm/v4/config/features"
 	fieldparams "github.com/prysmaticlabs/prysm/v4/config/fieldparams"
 	"github.com/prysmaticlabs/prysm/v4/config/params"
@@ -287,6 +288,7 @@ func TestServer_StreamChainHead_OnHeadUpdated(t *testing.T) {
 			CurrentJustifiedCheckPoint:  s.CurrentJustifiedCheckpoint(),
 			PreviousJustifiedCheckPoint: s.PreviousJustifiedCheckpoint()},
 		OptimisticModeFetcher: &chainMock.ChainService{},
+		SyncChecker:           &mockSync.Sync{IsSyncing: false},
 	}
 	exitRoutine := make(chan bool)
 	ctrl := gomock.NewController(t)
```
