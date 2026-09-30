# [?] api fix for panic on unsynced unfound block (#14063)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2024-05-31
Source: https://github.com/OffchainLabs/prysm/commit/836d369c6c91a9be1b1cfedf3ec17abdc850e01b
Type: security-commit

## Details
api fix for panic on unsynced unfound block (#14063)

* api fix for panic

* adding test

* fixing how we handle the error

## Patch
### beacon-chain/rpc/eth/beacon/handlers.go
```diff
@@ -60,16 +60,15 @@ func (s *Server) GetBlockV2(w http.ResponseWriter, r *http.Request) {
 		return
 	}
 	blk, err := s.Blocker.Block(ctx, []byte(blockId))
-	if err != nil {
-		shared.WriteBlockFetchError(w, blk, err)
+	if !shared.WriteBlockFetchError(w, blk, err) {
 		return
 	}
 
 	// Deal with block unblinding.
 	if blk.Version() >= version.Bellatrix && blk.IsBlinded() {
 		blk, err = s.ExecutionPayloadReconstructor.ReconstructFullBlock(ctx, blk)
 		if err != nil {
-			shared.WriteBlockFetchError(w, blk, errors.Wrapf(err, "could not reconstruct full execution payload to create signed beacon block"))
+			httputil.HandleError(w, errors.Wrapf(err, "could not reconstruct full execution payload to create signed beacon block").Error(), http.StatusBadRequest)
 			return
 		}
 	}
@@ -892,6 +891,11 @@ func (s *Server) validateConsensus(ctx context.Context, blk interfaces.ReadOnlyS
 	if err != nil {
 		return errors.Wrap(err, "could not get parent block")
 	}
+
+	if err := blocks.BeaconBlockIsNil(blk); err != nil {
+		return errors.Wrap(err, "could not validate block")
+	}
+
 	parentStateRoot := parentBlock.Block().StateRoot()
 	parentState, err := s.Stater.State(ctx, parentStateRoot[:])
 	if err != nil {
```

### beacon-chain/rpc/eth/beacon/handlers_test.go
```diff
@@ -86,6 +86,24 @@ func fillDBTestBlocks(ctx context.Context, t *testing.T, beaconDB db.Database) (
 }
 
 func TestGetBlockV2(t *testing.T) {
+	t.Run("Unsycned Block", func(t *testing.T) {
+		mockBlockFetcher := &testutil.MockBlocker{BlockToReturn: nil}
+		mockChainService := &chainMock.ChainService{
+			FinalizedRoots: map[[32]byte]bool{},
+		}
+		s := &Server{
+			FinalizationFetcher: mockChainService,
+			Blocker:             mockBlockFetcher,
+		}
+
+		request := httptest.NewRequest(http.MethodGet, "http://foo.example/eth/v2/beacon/blocks/{block_id}", nil)
+		request = mux.SetURLVars(request, map[string]string{"block_id": "123552314"})
+		writer := httptest.NewRecorder()
+		writer.Body = &bytes.Buffer{}
+
+		s.GetBlockV2(writer, request)
+		require.Equal(t, http.StatusNotFound, writer.Code)
+	})
 	t.Run("phase0", func(t *testing.T) {
 		b := util.NewBeaconBlock()
 		b.Block.Slot = 123
```

### beacon-chain/rpc/eth/rewards/handlers.go
```diff
@@ -14,6 +14,7 @@ import (
 	"github.com/prysmaticlabs/prysm/v5/beacon-chain/state"
 	fieldparams "github.com/prysmaticlabs/prysm/v5/config/fieldparams"
 	"github.com/prysmaticlabs/prysm/v5/config/params"
+	"github.com/prysmaticlabs/prysm/v5/consensus-types/blocks"
 	"github.com/prysmaticlabs/prysm/v5/consensus-types/primitives"
 	"github.com/prysmaticlabs/prysm/v5/network/httputil"
 	"github.com/prysmaticlabs/prysm/v5/runtime/version"
@@ -33,6 +34,12 @@ func (s *Server) BlockRewards(w http.ResponseWriter, r *http.Request) {
 	if !shared.WriteBlockFetchError(w, blk, err) {
 		return
 	}
+
+	if err := blocks.BeaconBlockIsNil(blk); err != nil {
+		httputil.HandleError(w, fmt.Sprintf("block id %s was not found", blockId), http.StatusNotFound)
+		return
+	}
+
 	if blk.Version() == version.Phase0 {
 		httputil.HandleError(w, "Block rewards are not supported for Phase 0 blocks", http.StatusBadRequest)
 		return
```
