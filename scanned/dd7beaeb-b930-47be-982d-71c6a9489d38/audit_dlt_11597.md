# [?] fix(checkpointing): proto-size accounting in checkpoint PrepareProposal repack (GHSA-692h-272j-rvgc) (#2023)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2026-08-04
Source: https://github.com/babylonlabs-io/babylon/commit/fcca3a65f72effaba3f57fb46ee76074f184e0b0
Type: security-commit

## Details
fix(checkpointing): proto-size accounting in checkpoint PrepareProposal repack (GHSA-692h-272j-rvgc) (#2023)

## Summary

Forward-port of the **GHSA-692h-272j-rvgc** (Immunefi #84812) security
fix from `release/v4.3.x` to `main`. The fix was merged directly to the
release branch (`a4d0f4b3`, "Merge commit from fork") and was missing
from `main`.

## The vulnerability

The checkpoint `PrepareProposal` repack (`x/checkpointing/prepare`)
bounded the injected-checkpoint proposal by raw `len(tx)`, but CometBFT
validates the returned proposal against the protobuf-encoded `Data.Txs`
size (`Txs.Validate` → `ComputeProtoSizeForTxs`), which is larger by
per-tx framing. A full block at a checkpoint (epoch) boundary could be
returned with `raw <= MaxTxBytes` while `proto > MaxTxBytes`, causing
CometBFT to panic the proposer ("transaction data size exceeds maximum")
and cascade to a chain halt.

## The fix

- Account for each tx by `ComputeProtoSizeForTxs([]Tx{tx})`, exactly the
per-tx quantity CometBFT's `Txs.Validate` accumulates, in
`SetOrReplaceCheckpointTx` and `ReplaceOtherTxs`, keeping
`PrepareProposal`'s budget in lockstep with what CometBFT enforces.
- Defense-in-depth guard in `PrepareProposal` that drops trailing
non-checkpoint txs while
`cmttypes.ToTxs(finalTxs).Validate(req.MaxTxBytes)` fails, delegating
the final check to CometBFT's own validator so the two cannot drift
apart again.
- Regression test for the `raw <= MaxTxBytes < proto` boundary, plus
updated size-accounting unit tests to proto sizes.

## Testing

- `go test ./x/checkpointing/prepare/...` passes.
- Verified `main`'s pre-existing vote-extension hardening in
`proposal.go` (`MaxVoteExtensionSize`, marshal round-trip check) is
preserved and coexists with this fix.

## Notes

- Cherry-picked cleanly from the release-branch commit `a4d0f4b3`
(`cherry-pick -x` reference preserved).
- Original advisory:
https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-692h-272j-rvgc

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### CHANGELOG.md
```diff
@@ -37,6 +37,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
 
 ## Unreleased
 
+### Bug Fixes
+
+- [GHSA-692h-272j-rvgc](https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-692h-272j-rvgc) fix(checkpointing): proto-size accounting in checkpoint PrepareProposal repack
+
 ### Improvements
 
 - [#2019](https://github.com/babylonlabs-io/babylon/pull/2019) chore(deps): bump github.com/opencontainers/runc from 1.2.8 to 1.3.6
```

### x/checkpointing/prepare/proposal.go
```diff
@@ -9,6 +9,7 @@ import (
 
 	"cosmossdk.io/log"
 	abci "github.com/cometbft/cometbft/abci/types"
+	cmttypes "github.com/cometbft/cometbft/types"
 	"github.com/cosmos/cosmos-sdk/baseapp"
 	"github.com/cosmos/cosmos-sdk/client"
 	codectypes "github.com/cosmos/cosmos-sdk/codec/types"
@@ -150,8 +151,25 @@ func (h *ProposalHandler) PrepareProposal() sdk.PrepareProposalHandler {
 			return &EmptyProposalRes, fmt.Errorf("failed to add other txs into the proposal: %w", err)
 		}
 
+		finalTxs := proposalTxs.GetTxsInOrder()
+
+		// Defense in depth: never return a proposal CometBFT will reject. We run the
+		// very same validator it applies to the txs we return (types.Txs.Validate,
+		// called from CreateProposalBlock), which panics the proposer in
+		// createProposalBlock on overflow. Delegating to it, rather than re-deriving
+		// the size rule here, is what stops the two from drifting apart again. The
+		// proto-size accounting in proposalTxs already guarantees the invariant; this
+		// guard drops trailing non-checkpoint txs so a future change that regresses
+		// that accounting still cannot crash the proposer. Validate enforces only the
+		// size limit today; were it ever to gain an unrelated check, the len > 1 bound
+		// still terminates this loop at a checkpoint-only proposal instead of
+		// spinning. The checkpoint tx (index 0) is always kept.
+		for len(finalTxs) > 1 && cmttypes.ToTxs(finalTxs).Validate(req.MaxTxBytes) != nil {
+			finalTxs = finalTxs[:len(finalTxs)-1]
+		}
+
 		return &abci.ResponsePrepareProposal{
-			Txs: proposalTxs.GetTxsInOrder(),
+			Txs: finalTxs,
 		}, nil
 	}
 }
```

### x/checkpointing/prepare/transactions.go
```diff
@@ -5,8 +5,24 @@ import (
 	"fmt"
 
 	abci "github.com/cometbft/cometbft/abci/types"
+	cmttypes "github.com/cometbft/cometbft/types"
 )
 
+// protoTxSize returns the number of bytes a single tx contributes to the block's
+// protobuf-encoded Data.Txs: len(tx) plus the repeated-field framing (tag byte +
+// length prefix). This is exactly the per-tx quantity CometBFT's Txs.Validate
+// accumulates and enforces against MaxTxBytes, so accounting for it here keeps
+// PrepareProposal's own budget in lockstep with the size CometBFT validates.
+// Accounting by raw len(tx) instead under-counts by the framing and lets a full
+// block over-shoot MaxTxBytes in proto terms, panicking the proposer.
+// An empty tx contributes nothing.
+func protoTxSize(tx []byte) uint64 {
+	if len(tx) == 0 {
+		return 0
+	}
+	return uint64(cmttypes.ComputeProtoSizeForTxs([]cmttypes.Tx{tx}))
+}
+
 // PrepareProposalTxs is used as an intermediary storage for transactions when creating
 // a proposal for `PrepareProposal`.
 type PrepareProposalTxs struct {
@@ -38,8 +54,8 @@ func NewPrepareProposalTxs(
 // SetOrReplaceCheckpointTx sets the tx used for checkpoint. If the checkpoint tx already exists,
 // replace it
 func (t *PrepareProposalTxs) SetOrReplaceCheckpointTx(tx []byte) error {
-	oldBytes := uint64(len(t.CheckpointTx))
-	newBytes := uint64(len(tx))
+	oldBytes := protoTxSize(t.CheckpointTx)
+	newBytes := protoTxSize(tx)
 	if err := t.updateUsedBytes(oldBytes, newBytes); err != nil {
 		return err
 	}
@@ -52,7 +68,7 @@ func (t *PrepareProposalTxs) ReplaceOtherTxs(allTxs [][]byte) error {
 	t.OtherTxs = make([][]byte, 0, len(allTxs))
 	bytesToAdd := uint64(0)
 	for _, tx := range allTxs {
-		txSize := uint64(len(tx))
+		txSize := protoTxSize(tx)
 		if t.UsedBytes+bytesToAdd+txSize > t.MaxBytes {
 			break
 		}
```

### x/checkpointing/prepare/transactions_test.go
```diff
@@ -4,6 +4,7 @@ import (
 	"testing"
 
 	abci "github.com/cometbft/cometbft/abci/types"
+	cmttypes "github.com/cometbft/cometbft/types"
 	"github.com/stretchr/testify/require"
 
 	"github.com/babylonlabs-io/babylon/v4/x/checkpointing/prepare"
@@ -24,19 +25,20 @@ func TestPrepareProposalTxs(t *testing.T) {
 		err = txs.SetOrReplaceCheckpointTx(checkpointTx)
 		require.NoError(t, err)
 
-		// Add other txs that fit within remaining space (80 bytes)
+		// Add other txs that fit within the remaining proto budget.
 		otherTxs := [][]byte{
-			make([]byte, 30), // tx1
-			make([]byte, 30), // tx2
-			make([]byte, 10), // tx3
+			make([]byte, 30), // tx1 (proto 32)
+			make([]byte, 30), // tx2 (proto 32)
+			make([]byte, 10), // tx3 (proto 12)
 		}
 		err = txs.ReplaceOtherTxs(otherTxs)
 		require.NoError(t, err)
 
-		// Verify all txs were added
+		// Verify all txs were added. UsedBytes is the protobuf Data.Txs size
+		// (raw + per-tx framing): 22 + 32 + 32 + 12 = 98.
 		allTxs := txs.GetTxsInOrder()
 		require.Equal(t, 4, len(allTxs)) // checkpoint + 3 other txs
-		require.Equal(t, uint64(90), txs.UsedBytes)
+		require.Equal(t, uint64(98), txs.UsedBytes)
 	})
 
 	t.Run("partial addition - some transactions exceed limit", func(t *testing.T) {
@@ -53,19 +55,20 @@ func TestPrepareProposalTxs(t *testing.T) {
 		err = txs.SetOrReplaceCheckpointTx(checkpointTx)
 		require.NoError(t, err)
 
-		// Try to add other txs where some won't fit
+		// Try to add other txs where some won't fit (proto sizes shown)
 		otherTxs := [][]byte{
-			make([]byte, 20), // tx1 - fits
-			make([]byte, 20), // tx2 - won't fit
-			make([]byte, 10), // tx3 - won't fit
+			make([]byte, 20), // tx1 (proto 22) - fits
+			make([]byte, 20), // tx2 (proto 22) - won't fit
+			make([]byte, 10), // tx3 (proto 12) - won't fit
 		}
 		err = txs.ReplaceOtherTxs(otherTxs)
 		require.NoError(t, err)
 
-		// Verify only fitting txs were added
+		// Verify only fitting txs were added. Proto: checkpoint 22 + tx1 22 = 44;
+		// tx2 would make 66 > 50, so it and tx3 are dropped.
 		allTxs := txs.GetTxsInOrder()
 		require.Equal(t, 2, len(allTxs)) // checkpoint + tx1
-		require.Equal(t, uint64(40), txs.UsedBytes)
+		require.Equal(t, uint64(44), txs.UsedBytes)
 	})
 
 	t.Run("full addition - transactions fill space exactly", func(t *testing.T) {
@@ -77,20 +80,21 @@ func TestPrepareProposalTxs(t *testing.T) {
 		txs, err := prepare.NewPrepareProposalTxs(req)
 		require.NoError(t, err)
 
-		// Set checkpoint tx of size 40
-		checkpointTx := make([]byte, 40)
+		// Set checkpoint tx of size 38 (proto 40)
+		checkpointTx := make([]byte, 38)
 		err = txs.SetOrReplaceCheckpointTx(checkpointTx)
 		require.NoError(t, err)
 
-		// Add other txs that exactly fill remaining space (60 bytes)
+		// Add other txs whose proto sizes exactly fill the remaining space:
+		// 40 + 30 + 30 = 100.
 		otherTxs := [][]byte{
-			make([]byte, 30), // tx1
-			make([]byte, 30), // tx2
+			make([]byte, 28), // tx1 (proto 30)
+			make([]byte, 28), // tx2 (proto 30)
 		}
 		err = txs.ReplaceOtherTxs(otherTxs)
 		require.NoError(t, err)
 
-		// Verify all txs were added and space is exactly filled
+		// Verify all txs were added and the proto budget is exactly filled.
 		allTxs := txs.GetTxsInOrder()
 		require.Equal(t, 3, len(allTxs)) // checkpoint + 2 other txs
 		require.Equal(t, maxBytes, txs.UsedBytes)
@@ -121,4 +125,50 @@ func TestPrepareProposalTxs(t *testing.T) {
 		require.Error(t, err)
 		require.Contains(t, err.Error(), "must be positive")
 	})
+
+	// Regression for GHSA-692h-272j-rvgc: a set whose RAW byte sum fits MaxTxBytes
+	// but whose protobuf Data.Txs size (raw + per-tx framing) does not. The old
+	// raw-len accounting returned the whole set, and CometBFT's Txs.Validate
+	// (which sums ComputeProtoSizeForTxs) then panicked the proposer building the
+	// block. The proposal we return must never exceed MaxTxBytes in proto terms.
+	t.Run("regression GHSA-692h-272j-rvgc - proto size never exceeds MaxTxBytes", func(t *testing.T) {
+		maxBytes := uint64(100)
+		req := &abci.RequestPrepareProposal{MaxTxBytes: int64(maxBytes)}
+
+		txs, err := prepare.NewPrepareProposalTxs(req)
+		require.NoError(t, err)
+
+		checkpointTx := make([]byte, 8) // proto 10
+		require.NoError(t, txs.SetOrReplaceCheckpointTx(checkpointTx))
+
+		otherTxs := [][]byte{
+			make([]byte, 22), // proto 24
+			make([]byte, 22),
+			make([]byte, 22),
+			make([]byte, 22),
+		}
+
+		// Precondition that reproduces the bug: raw fits, proto does not.
+		candidate := append([][]byte{checkpointTx}, otherTxs...)
+		rawSum := 0
+		for _, tx := range candidate {
+			rawSum += len(tx)
+		}
+		require.LessOrEqual(t, uint64(rawSum), maxBytes,
+			"raw sum must fit — this is what the buggy raw-len accounting saw")
+		require.Greater(t, cmttypes.ComputeProtoSizeForTxs(cmttypes.ToTxs(candidate)), int64(maxBytes),
+			"proto sum must exceed — this is what CometBFT's Txs.Validate rejects")
+
+		require.NoError(t, txs.ReplaceOtherTxs(otherTxs))
+		got := txs.GetTxsInOrder()
+
+		// The fix must keep the returned proposal within MaxTxBytes in PROTO terms,
+		// exactly the invariant CometBFT enforces, so the proposer never returns a
+		// block it will then panic building.
+		require.LessOrEqual(t, cmttypes.ComputeProtoSizeForTxs(cmttypes.ToTxs(got)), int64(maxBytes),
+			"returned proposal must fit MaxTxBytes in proto terms")
+		require.LessOrEqual(t, txs.UsedBytes, maxBytes)
+		require.Less(t, len(got), len(candidate), "the overflowing tx must be dropped")
+		require.Equal(t, checkpointTx, got[0], "the checkpoint tx must be kept")
+	})
 }
```
