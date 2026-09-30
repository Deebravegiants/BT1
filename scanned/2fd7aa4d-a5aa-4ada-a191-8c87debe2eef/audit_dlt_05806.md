# [?] Fix off-by-one in PushBlock that causes nil dereference panic (#2924)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-02-20
Source: https://github.com/sei-protocol/sei-chain/commit/933111a74ee921e7ea8ccc915c7cea337b5cd052
Type: security-commit

## Details
Fix off-by-one in PushBlock that causes nil dereference panic (#2924)

## Summary

- **Fix off-by-one in `PushBlock`**: The `WaitUntil` condition used `n
<= inner.nextQC`, which allows `PushBlock` to proceed when `n ==
nextQC`. Since `inner.qcs` stores entries for the half-open range
`[first, nextQC)`, the map lookup returns `nil`, and the subsequent
`qc.Headers()` call panics with a nil pointer dereference. Changed to `n
< inner.nextQC` to match every other waiter in the file (`QC`, `Block`,
`GlobalBlock`, `AppProposal`).

---------

Co-authored-by: Cursor <cursoragent@cursor.com>
Co-authored-by: Masih H. Derkani <m@derkani.org>

## Patch
### sei-tendermint/internal/autobahn/data/state.go
```diff
@@ -195,7 +195,7 @@ func (s *State) PushBlock(ctx context.Context, n types.GlobalBlockNumber, block
 		return fmt.Errorf("block.Verify(): %w", err)
 	}
 	for inner, ctrl := range s.inner.Lock() {
-		if err := ctrl.WaitUntil(ctx, func() bool { return n <= inner.nextQC }); err != nil {
+		if err := ctrl.WaitUntil(ctx, func() bool { return n < inner.nextQC }); err != nil {
 			return err
 		}
 		// Early exit if we already have the block.
```

### sei-tendermint/internal/autobahn/data/state_test.go
```diff
@@ -6,6 +6,7 @@ import (
 	"fmt"
 	"maps"
 	"testing"
+	"testing/synctest"
 	"time"
 
 	"github.com/sei-protocol/sei-chain/sei-tendermint/internal/autobahn/types"
@@ -299,3 +300,73 @@ func TestExecution(t *testing.T) {
 		t.Fatal(err)
 	}
 }
+
+func TestPushBlockAcceptsBlockWithQC(t *testing.T) {
+	ctx := t.Context()
+	rng := utils.TestRng()
+	committee, keys := types.GenCommittee(rng, 3)
+
+	state := NewState(&Config{
+		Committee: committee,
+	}, utils.None[BlockStore]())
+
+	// Push QC without blocks.
+	qc, blocks := TestCommitQC(rng, committee, keys, utils.None[*types.CommitQC]())
+	require.NoError(t, state.PushQC(ctx, qc, nil))
+	gr := qc.QC().GlobalRange()
+
+	// PushBlock for a block whose QC is already present succeeds immediately.
+	require.NoError(t, state.PushBlock(ctx, gr.First, blocks[0]))
+	got, err := state.TryBlock(gr.First)
+	require.NoError(t, err)
+	require.Equal(t, blocks[0], got)
+}
+
+func TestPushBlockWaitsForQC(t *testing.T) {
+	synctest.Test(t, func(t *testing.T) {
+		ctx := t.Context()
+		rng := utils.TestRng()
+		committee, keys := types.GenCommittee(rng, 3)
+
+		state := NewState(&Config{
+			Committee: committee,
+		}, utils.None[BlockStore]())
+
+		// Push first QC covering [0, N).
+		qc1, blocks1 := TestCommitQC(rng, committee, keys, utils.None[*types.CommitQC]())
+		require.NoError(t, state.PushQC(ctx, qc1, blocks1))
+
+		// Prepare second QC covering [N, M) but don't push it yet.
+		qc2, blocks2 := TestCommitQC(rng, committee, keys, utils.Some(qc1.QC()))
+		gr2 := qc2.QC().GlobalRange()
+
+		// Block gr2.First should not be in state yet.
+		_, err := state.TryBlock(gr2.First)
+		require.ErrorIs(t, err, ErrNotFound)
+
+		// PushBlock for a block in qc2's range. With the off-by-one bug
+		// (n <= inner.nextQC), this would immediately dereference a nil QC
+		// pointer and panic. With the fix, it waits for the QC.
+		var pushErr error
+		go func() {
+			pushErr = state.PushBlock(ctx, gr2.First, blocks2[0])
+		}()
+
+		// Wait for PushBlock to become durably blocked on the QC channel.
+		synctest.Wait()
+
+		// Block should still not be in state (PushBlock is blocked).
+		_, err = state.TryBlock(gr2.First)
+		require.ErrorIs(t, err, ErrNotFound)
+
+		// Push qc2 to unblock PushBlock.
+		require.NoError(t, state.PushQC(ctx, qc2, nil))
+		synctest.Wait()
+		require.NoError(t, pushErr)
+
+		// Block gr2.First should now be in state.
+		got, err := state.TryBlock(gr2.First)
+		require.NoError(t, err)
+		require.Equal(t, blocks2[0], got)
+	})
+}
```
