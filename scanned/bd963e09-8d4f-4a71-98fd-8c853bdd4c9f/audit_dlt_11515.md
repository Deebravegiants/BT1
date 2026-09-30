# [?] fix(app): drop malformed blob txs in separateTxs instead of panicking (#7202)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-05-04
Source: https://github.com/celestiaorg/celestia-app/commit/3391359745f0c511cdca66c1c811fb78c0dc94b3
Type: security-commit

## Details
fix(app): drop malformed blob txs in separateTxs instead of panicking (#7202)

## Summary

- Drop malformed blob txs in `separateTxs` instead of panicking,
matching `ProcessProposalHandler`'s behavior on the same input.
- Log the dropped tx and increment a
`prepare_proposal/malformed_blob_txs` telemetry counter so a regression
in CheckTx filtering remains visible (replaces the alarm role the panic
was playing).
- Add a regression test that constructs the malformed input and asserts
it is dropped without panicking.

Closes https://linear.app/celestia/issue/PROTOCO-1668

## Test plan

- [x] `go test -v -run TestSeparateTxs ./app/` passes including the new
`malformed blob tx with no blobs is dropped without panicking` case
- [x] `go test -tags fibre -run TestSeparateTxs ./app/` passes
- [x] `make build`
- [x] `make lint` (golangci-lint with and without `-tags fibre`)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### app/filtered_square_builder.go
```diff
@@ -1,6 +1,7 @@
 package app
 
 import (
+	"cosmossdk.io/log"
 	"github.com/celestiaorg/celestia-app/v9/pkg/appconsts"
 	square "github.com/celestiaorg/go-square/v4"
 	"github.com/celestiaorg/go-square/v4/tx"
@@ -69,7 +70,7 @@ func (fsb *FilteredSquareBuilder) Fill(ctx sdk.Context, txs [][]byte, maxTxBytes
 	}
 
 	// note that there is an additional filter step for tx size of raw txs here
-	normalTxs, blobTxs, payForFibreTxs := separateTxs(fsb.txConfig, filteredByMaxBytes)
+	normalTxs, blobTxs, payForFibreTxs := separateTxs(logger, fsb.txConfig, filteredByMaxBytes)
 
 	var (
 		sdkMessageCount = 0
@@ -210,7 +211,7 @@ func encodeBlobTxs(blobTxs []*tx.BlobTx) [][]byte {
 //
 // When the fibre build tag is not set, countMsgPayForFibre always returns 0, so
 // the payForFibreTxs slice is always empty.
-func separateTxs(txConfig client.TxConfig, rawTxs [][]byte) (normalTxs [][]byte, blobTxs []*tx.BlobTx, payForFibreTxs [][]byte) {
+func separateTxs(logger log.Logger, txConfig client.TxConfig, rawTxs [][]byte) (normalTxs [][]byte, blobTxs []*tx.BlobTx, payForFibreTxs [][]byte) {
 	normalTxs = make([][]byte, 0, len(rawTxs))
 	blobTxs = make([]*tx.BlobTx, 0, len(rawTxs))
 	payForFibreTxs = make([][]byte, 0, len(rawTxs))
@@ -227,7 +228,12 @@ func separateTxs(txConfig client.TxConfig, rawTxs [][]byte) (normalTxs [][]byte,
 		bTx, isBlob, err := tx.UnmarshalBlobTx(rawTx)
 		if isBlob {
 			if err != nil {
-				panic(err)
+				// Drop malformed blob txs. Matches ProcessProposalHandler.
+				// CheckTx should have rejected this; reaching here indicates a
+				// regression so log + count it for visibility.
+				logger.Error("dropping malformed blob tx", "tx", tmbytes.HexBytes(coretypes.Tx(rawTx).Hash()), "err", err)
+				telemetry.IncrCounter(1, "prepare_proposal", "malformed_blob_txs")
+				continue
 			}
 			blobTxs = append(blobTxs, bTx)
 			continue
```

### app/filtered_square_builder_fibre_test.go
```diff
@@ -79,7 +79,7 @@ func TestSeparateTxsFibre(t *testing.T) {
 
 	for _, tc := range tests {
 		t.Run(tc.name, func(t *testing.T) {
-			normalTxs, blobTxs, payForFibreTxs := separateTxs(txConfig, tc.rawTxs)
+			normalTxs, blobTxs, payForFibreTxs := separateTxs(log.NewNopLogger(), txConfig, tc.rawTxs)
 			require.Len(t, normalTxs, tc.wantNorm)
 			require.Len(t, blobTxs, tc.wantBlob)
 			require.Len(t, payForFibreTxs, tc.wantPFF)
```

### app/filtered_square_builder_test.go
```diff
@@ -12,6 +12,7 @@ import (
 	"github.com/celestiaorg/celestia-app/v9/pkg/appconsts"
 	"github.com/celestiaorg/celestia-app/v9/test/util/blobfactory"
 	blobtypes "github.com/celestiaorg/celestia-app/v9/x/blob/types"
+	"github.com/celestiaorg/go-square/v4/proto/blob/v4"
 	"github.com/celestiaorg/go-square/v4/share"
 	"github.com/celestiaorg/go-square/v4/tx"
 	cmtproto "github.com/cometbft/cometbft/proto/tendermint/types"
@@ -21,6 +22,7 @@ import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	banktypes "github.com/cosmos/cosmos-sdk/x/bank/types"
 	"github.com/stretchr/testify/require"
+	"google.golang.org/protobuf/proto"
 )
 
 func TestSeparateTxs(t *testing.T) {
@@ -65,18 +67,35 @@ func TestSeparateTxs(t *testing.T) {
 			wantBlob: 0,
 			wantPFF:  0,
 		},
+		{
+			// A proto-valid v4.BlobTx with TypeId="BLOB" but no blobs causes
+			// UnmarshalBlobTx to return (isBlob=true, err!=nil). The function
+			// must drop it instead of panicking.
+			name:     "malformed blob tx with no blobs is dropped without panicking",
+			rawTxs:   [][]byte{mustMarshal(t, &v4.BlobTx{TypeId: "BLOB"})},
+			wantNorm: 0,
+			wantBlob: 0,
+			wantPFF:  0,
+		},
 	}
 
 	for _, tc := range tests {
 		t.Run(tc.name, func(t *testing.T) {
-			normalTxs, blobTxs, payForFibreTxs := separateTxs(txConfig, tc.rawTxs)
+			normalTxs, blobTxs, payForFibreTxs := separateTxs(log.NewNopLogger(), txConfig, tc.rawTxs)
 			require.Len(t, normalTxs, tc.wantNorm)
 			require.Len(t, blobTxs, tc.wantBlob)
 			require.Len(t, payForFibreTxs, tc.wantPFF)
 		})
 	}
 }
 
+func mustMarshal(t *testing.T, m proto.Message) []byte {
+	t.Helper()
+	b, err := proto.Marshal(m)
+	require.NoError(t, err)
+	return b
+}
+
 // newNormalTx creates an unsigned MsgSend transaction for testing.
 func newNormalTx(t *testing.T, txConfig client.TxConfig) []byte {
 	t.Helper()
```
