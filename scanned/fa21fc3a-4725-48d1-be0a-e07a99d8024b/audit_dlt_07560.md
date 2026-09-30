# [?] Fix dag_getHeads panic at epoch boundaries (#1181)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2026-09-18
Source: https://github.com/0xsoniclabs/sonic/commit/b7dd756d6c67d18721db10ac8737e7ca2db89917
Type: security-commit

## Details
Fix dag_getHeads panic at epoch boundaries (#1181)

dag_getHeads resolved the requested epoch against the block-epoch state
and then read that epoch's heads from the epoch store. Epoch sealing
publishes the new block-epoch state before switchEpochTo swaps the epoch
store, so the resolved epoch briefly had no epoch store, GetHeads
returned nil and GetHeadsSlice dereferenced it.

Read the heads through Store.GetHeads, which reports a missing epoch
store as nil, and turn that into an error naming the requested epoch
instead of pre-checking it against a value that can disagree with the
store. Which epochs the method serves is unchanged: only the open one,
selected as pending or by its number. The doc comments now say so using
the selector names, as their -1/-2 numbering predates the current
go-ethereum constants and was inverted.

Co-authored-by: Claude Opus 5 (1M context) <noreply@anthropic.com>

## Patch
### api/ethapi/dag_api.go
```diff
@@ -65,8 +65,9 @@ func (s *PublicDAGChainAPI) GetEventPayload(ctx context.Context, shortEventID st
 }
 
 // GetHeads returns IDs of all the epoch events with no descendants.
-// * When epoch is -2 the heads for latest epoch are returned.
-// * When epoch is -1 the heads for latest sealed epoch are returned.
+// Heads are only kept for the open epoch, selected as pending or by its
+// number. Sealed epochs, including latest (the latest sealed one), are
+// rejected.
 func (s *PublicDAGChainAPI) GetHeads(ctx context.Context, epoch rpc.BlockNumber) ([]hexutil.Bytes, error) {
 	res, err := s.b.GetHeads(ctx, epoch)
 
```

### gossip/ethapi_backend.go
```diff
@@ -264,29 +264,27 @@ func (b *EthAPIBackend) GetEvent(ctx context.Context, shortEventID string) (*int
 	return b.svc.store.GetEvent(id), nil
 }
 
-// GetHeads returns IDs of all the epoch events with no descendants.
-// * When epoch is -2 the heads for latest epoch are returned.
-// * When epoch is -1 the heads for latest sealed epoch are returned.
-func (b *EthAPIBackend) GetHeads(ctx context.Context, epoch rpc.BlockNumber) (heads hash.Events, err error) {
-	current := b.svc.store.GetEpoch()
+var errHeadsUnavailable = stderrors.New("heads are not available")
 
+// GetHeads returns IDs of all the epoch events with no descendants.
+// Heads are only kept for the open epoch, selected as pending or by its
+// number. Sealed epochs, including latest (the latest sealed one), fail
+// with errHeadsUnavailable.
+func (b *EthAPIBackend) GetHeads(ctx context.Context, epoch rpc.BlockNumber) (hash.Events, error) {
 	requested, err := b.epochWithDefault(ctx, epoch)
 	if err != nil {
 		return nil, err
 	}
 
-	if requested == current {
-		heads = b.svc.store.GetHeadsSlice(requested)
-	} else {
-		err = errors.New("heads for previous epochs are not available")
-		return
-	}
-
+	// The epoch may seal between resolving it and reading its heads, so the
+	// store is the only authority on their availability.
+	heads := b.svc.store.GetHeads(requested)
 	if heads == nil {
-		heads = hash.Events{}
+		return nil, fmt.Errorf("epoch %d: %w", requested, errHeadsUnavailable)
 	}
-
-	return
+	heads.RLock()
+	defer heads.RUnlock()
+	return heads.Val.Slice(), nil
 }
 
 func (b *EthAPIBackend) epochWithDefault(ctx context.Context, epoch rpc.BlockNumber) (requested idx.Epoch, err error) {
```

### gossip/ethapi_backend_test.go
```diff
@@ -25,6 +25,8 @@ import (
 	"github.com/0xsoniclabs/sonic/inter"
 	"github.com/0xsoniclabs/sonic/inter/iblockproc"
 	"github.com/0xsoniclabs/sonic/opera"
+	"github.com/0xsoniclabs/sonic/utils/concurrent"
+	"github.com/Fantom-foundation/lachesis-base/hash"
 	"github.com/Fantom-foundation/lachesis-base/inter/idx"
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/core/types"
@@ -310,3 +312,50 @@ func TestEthApiBackend_epochWithDefault_RejectsEpochsAboveUint32Max(t *testing.T
 	_, err = backend.epochWithDefault(t.Context(), outOfRange)
 	require.Error(t, err, "epoch value above uint32 max must be rejected")
 }
+
+func newBackendAtEpoch(t *testing.T, epoch idx.Epoch) (*Store, *EthAPIBackend) {
+	store, err := NewMemStore(t)
+	require.NoError(t, err)
+	store.SetBlockEpochState(iblockproc.BlockState{}, iblockproc.EpochState{Epoch: epoch})
+	store.loadEpochStore(epoch)
+	return store, &EthAPIBackend{svc: &Service{store: store}}
+}
+
+func TestEthApiBackend_GetHeads_ReturnsHeadsOfOpenEpoch(t *testing.T) {
+	const epoch = idx.Epoch(3)
+	store, backend := newBackendAtEpoch(t, epoch)
+
+	want := hash.Events{hash.BytesToEvent([]byte{1}), hash.BytesToEvent([]byte{2})}
+	store.SetHeads(epoch, concurrent.WrapEventsSet(want.Set()))
+
+	for _, selector := range []rpc.BlockNumber{rpc.BlockNumber(epoch), rpc.PendingBlockNumber} {
+		got, err := backend.GetHeads(t.Context(), selector)
+		require.NoError(t, err, selector)
+		require.ElementsMatch(t, want, got, selector)
+	}
+}
+
+func TestEthApiBackend_GetHeads_ReportsUnavailableHeadsForSealedEpoch(t *testing.T) {
+	const epoch = idx.Epoch(3)
+	_, backend := newBackendAtEpoch(t, epoch)
+
+	for _, sealed := range []rpc.BlockNumber{rpc.BlockNumber(epoch - 1), rpc.LatestBlockNumber} {
+		_, err := backend.GetHeads(t.Context(), sealed)
+		require.ErrorIs(t, err, errHeadsUnavailable, sealed)
+	}
+}
+
+func TestEthApiBackend_GetHeads_ReportsUnavailableHeadsWhileEpochStoreLagsBehindEpochState(t *testing.T) {
+	const epoch = idx.Epoch(3)
+	store, backend := newBackendAtEpoch(t, epoch)
+
+	// Sealing publishes the new epoch state before switchEpochTo swaps the
+	// epoch store, so the open epoch briefly has no epoch store at all.
+	store.SetBlockEpochState(iblockproc.BlockState{}, iblockproc.EpochState{Epoch: epoch + 1})
+
+	var err error
+	require.NotPanics(t, func() {
+		_, err = backend.GetHeads(t.Context(), rpc.PendingBlockNumber)
+	})
+	require.ErrorIs(t, err, errHeadsUnavailable)
+}
```
