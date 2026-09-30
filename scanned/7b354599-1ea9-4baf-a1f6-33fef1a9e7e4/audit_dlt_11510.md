# [?] fix: fibre codex resource exhaustion

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-08-27
Source: https://github.com/celestiaorg/celestia-app/commit/ec0df54bdafe1b14978cf26a44b745fbbd4f733d
Type: security-commit

## Details
fix: fibre codex resource exhaustion

## Patch
### fibre/decode_limits_test.go
```diff
@@ -0,0 +1,22 @@
+package fibre
+
+import (
+	"math/bits"
+	"testing"
+
+	"github.com/celestiaorg/celestia-app/v10/x/fibre/types"
+	"github.com/stretchr/testify/require"
+)
+
+// TestDecodeLimitsMatchParams guards the hardcoded codec cardinality bounds in
+// x/fibre/types against drift from the protocol parameters they are derived from.
+func TestDecodeLimitsMatchParams(t *testing.T) {
+	p := DefaultProtocolParams
+
+	require.Equal(t, p.MaxRowsPerValidator(), types.MaxBlobRowsPerShard,
+		"MaxBlobRowsPerShard must equal MaxRowsPerValidator")
+
+	treeDepth := bits.Len(uint(p.TotalRows() - 1))
+	require.Equal(t, treeDepth, types.MaxProofSegmentsPerRow,
+		"MaxProofSegmentsPerRow must equal the Merkle tree depth ceil(log2(TotalRows))")
+}
```

### fibre/internal/grpc/codec.go
```diff
@@ -70,5 +70,14 @@ func (c *pooledCodec) Unmarshal(data mem.BufferSlice, v any) error {
 	if data.Len() == 0 {
 		return msg.Unmarshal(nil)
 	}
-	return msg.Unmarshal(data.Materialize())
+	buf := data.Materialize()
+	// Bound repeated-field cardinality before the generated decoder allocates
+	// per-row and per-proof objects, so a compact malicious UploadShardRequest
+	// cannot amplify into large decoded memory. See validateUploadShardCardinality.
+	if _, ok := v.(*types.UploadShardRequest); ok {
+		if err := validateUploadShardCardinality(buf); err != nil {
+			return err
+		}
+	}
+	return msg.Unmarshal(buf)
 }
```

### fibre/internal/grpc/codec_decode.go
```diff
@@ -0,0 +1,76 @@
+package grpc
+
+import (
+	"fmt"
+
+	"github.com/celestiaorg/celestia-app/v10/x/fibre/types"
+	"google.golang.org/protobuf/encoding/protowire"
+)
+
+// This file bounds the repeated-field cardinality of an UploadShardRequest
+// before the generated protobuf decoder runs. The decoder allocates a heap
+// object per row and a slice entry per proof segment with no upper bound, so a
+// compact message (an empty BlobRow is ~2 wire bytes) could otherwise amplify
+// into decoded memory far beyond its wire size and exhaust server memory. The
+// pre-scan allocates nothing: it counts field occurrences and skips values.
+
+// validateUploadShardCardinality rejects UploadShardRequest wire bytes whose
+// BlobShard.Rows or BlobRow.Proof cardinality exceeds its protocol bound.
+func validateUploadShardCardinality(data []byte) error {
+	return scanBytesField(data, uploadShardRequestFieldShard, validateBlobShardCardinality)
+}
+
+func validateBlobShardCardinality(shard []byte) error {
+	rows := 0
+	return scanBytesField(shard, blobShardFieldRows, func(row []byte) error {
+		rows++
+		if rows > types.MaxBlobRowsPerShard {
+			return fmt.Errorf("fibre-proto codec: shard exceeds %d rows", types.MaxBlobRowsPerShard)
+		}
+		return validateBlobRowCardinality(row)
+	})
+}
+
+func validateBlobRowCardinality(row []byte) error {
+	proofs := 0
+	return scanBytesField(row, blobRowFieldProof, func([]byte) error {
+		proofs++
+		if proofs > types.MaxProofSegmentsPerRow {
+			return fmt.Errorf("fibre-proto codec: row exceeds %d proof segments", types.MaxProofSegmentsPerRow)
+		}
+		return nil
+	})
+}
+
+// scanBytesField walks a proto message's wire bytes, calling visit with the
+// payload of every occurrence of the length-delimited field num and skipping
+// all other fields. It returns visit's first error, or a wire error for
+// malformed bytes.
+func scanBytesField(data []byte, num protowire.Number, visit func(payload []byte) error) error {
+	for len(data) > 0 {
+		fieldNum, typ, n := protowire.ConsumeTag(data)
+		if n < 0 {
+			return protowire.ParseError(n)
+		}
+		data = data[n:]
+
+		if fieldNum == num && typ == protowire.BytesType {
+			payload, n := protowire.ConsumeBytes(data)
+			if n < 0 {
+				return protowire.ParseError(n)
+			}
+			if err := visit(payload); err != nil {
+				return err
+			}
+			data = data[n:]
+			continue
+		}
+
+		n = protowire.ConsumeFieldValue(fieldNum, typ, data)
+		if n < 0 {
+			return protowire.ParseError(n)
+		}
+		data = data[n:]
+	}
+	return nil
+}
```

### fibre/internal/grpc/codec_decode_test.go
```diff
@@ -0,0 +1,109 @@
+package grpc
+
+import (
+	"testing"
+
+	"github.com/celestiaorg/celestia-app/v10/x/fibre/types"
+	"github.com/stretchr/testify/require"
+	"google.golang.org/grpc/mem"
+	"google.golang.org/protobuf/encoding/protowire"
+)
+
+// makeUploadShard builds an UploadShardRequest with rows rows of proofsPerRow
+// proof segments each. Rows carry data and the shard carries RLCs so the
+// cardinality scan's skip paths are exercised; only the repeated-field counts
+// matter to the limits.
+func makeUploadShard(rows, proofsPerRow int) *types.UploadShardRequest {
+	proof := make([][]byte, proofsPerRow)
+	for i := range proof {
+		proof[i] = make([]byte, 32)
+	}
+	blobRows := make([]*types.BlobRow, rows)
+	for i := range blobRows {
+		blobRows[i] = &types.BlobRow{Index: uint32(i), Data: []byte{0xff}, Proof: proof}
+	}
+	return &types.UploadShardRequest{Shard: &types.BlobShard{Rows: blobRows, Rlcs: make([]byte, 16)}}
+}
+
+func marshalUploadShard(t *testing.T, req *types.UploadShardRequest) []byte {
+	t.Helper()
+	buf, err := req.Marshal()
+	require.NoError(t, err)
+	return buf
+}
+
+func TestValidateUploadShardCardinality(t *testing.T) {
+	tests := []struct {
+		name         string
+		rows         int
+		proofsPerRow int
+		wantErr      string
+	}{
+		{name: "empty request"},
+		{name: "at row and proof limits", rows: types.MaxBlobRowsPerShard, proofsPerRow: types.MaxProofSegmentsPerRow},
+		{name: "one row over limit", rows: types.MaxBlobRowsPerShard + 1, proofsPerRow: 1, wantErr: "rows"},
+		{name: "one proof over limit", rows: 1, proofsPerRow: types.MaxProofSegmentsPerRow + 1, wantErr: "proof segments"},
+	}
+
+	for _, tc := range tests {
+		t.Run(tc.name, func(t *testing.T) {
+			err := validateUploadShardCardinality(marshalUploadShard(t, makeUploadShard(tc.rows, tc.proofsPerRow)))
+			if tc.wantErr != "" {
+				require.ErrorContains(t, err, tc.wantErr)
+			} else {
+				require.NoError(t, err)
+			}
+		})
+	}
+
+	t.Run("only last row over proof limit", func(t *testing.T) {
+		req := makeUploadShard(3, 1)
+		req.Shard.Rows[2].Proof = make([][]byte, types.MaxProofSegmentsPerRow+1)
+		err := validateUploadShardCardinality(marshalUploadShard(t, req))
+		require.ErrorContains(t, err, "proof segments")
+	})
+
+	t.Run("unknown trailing field skipped", func(t *testing.T) {
+		buf := marshalUploadShard(t, makeUploadShard(1, 1))
+		buf = protowire.AppendTag(buf, 7, protowire.VarintType)
+		buf = protowire.AppendVarint(buf, 42)
+		require.NoError(t, validateUploadShardCardinality(buf))
+	})
+
+	t.Run("truncated bytes rejected", func(t *testing.T) {
+		buf := marshalUploadShard(t, makeUploadShard(2, 2))
+		require.Error(t, validateUploadShardCardinality(buf[:len(buf)-1]))
+	})
+
+	t.Run("malformed tag rejected", func(t *testing.T) {
+		require.Error(t, validateUploadShardCardinality([]byte{0x80}))
+	})
+
+	t.Run("tag without value rejected", func(t *testing.T) {
+		require.Error(t, validateUploadShardCardinality(protowire.AppendTag(nil, 7, protowire.VarintType)))
+	})
+}
+
+// TestCodecUnmarshalBoundsCardinality verifies the codec rejects an
+// over-cardinality UploadShardRequest before the generated decoder allocates,
+// and that a maximal valid request round-trips through the codec's own
+// scatter marshaler.
+func TestCodecUnmarshalBoundsCardinality(t *testing.T) {
+	codec := &pooledCodec{pool: mem.DefaultBufferPool()}
+
+	t.Run("rejects amplified request", func(t *testing.T) {
+		buf := marshalUploadShard(t, makeUploadShard(types.MaxBlobRowsPerShard+1, 0))
+		err := codec.Unmarshal(mem.BufferSlice{mem.SliceBuffer(buf)}, &types.UploadShardRequest{})
+		require.ErrorContains(t, err, "rows")
+	})
+
+	t.Run("round-trips a valid request", func(t *testing.T) {
+		wire, err := codec.Marshal(makeUploadShard(2, types.MaxProofSegmentsPerRow))
+		require.NoError(t, err)
+
+		var got types.UploadShardRequest
+		require.NoError(t, codec.Unmarshal(wire, &got))
+		require.Len(t, got.Shard.Rows, 2)
+		require.Len(t, got.Shard.Rows[1].Proof, types.MaxProofSegmentsPerRow)
+	})
+}
```

### fibre/internal/grpc/server.go
```diff
@@ -21,6 +21,11 @@ import (
 // maxConnections * maxConcurrentStreams * MaxRecvMsgSize (~27 GiB). The values
 // are intentionally conservative for a 32 GiB-RAM validator. Tying them to
 // staking power, or adding a per-peer connection policy, are possible follow-ups.
+//
+// Decoded memory is bounded separately: the fibre-proto codec caps repeated-row
+// and per-row-proof cardinality before the decoder allocates, so a compact
+// message cannot amplify into decoded memory beyond its wire size (see
+// validateUploadShardCardinality in codec_decode.go).
 const (
 	maxConnections       = 16
 	maxConcurrentStreams = 13
```

### x/fibre/types/limits.go
```diff
@@ -0,0 +1,20 @@
+package types
+
+// Decode-time cardinality bounds for a BlobShard. The fibre-proto codec enforces
+// them before the protobuf decoder allocates per-row and per-proof objects, so a
+// peer cannot amplify a compact message (an empty BlobRow is ~2 wire bytes but a
+// live heap object) into large decoded memory.
+//
+// The values are the protocol v0 maxima. TestDecodeLimitsMatchParams in the fibre
+// package asserts they stay in sync with ProtocolParams.
+const (
+	// MaxBlobRowsPerShard bounds BlobShard.Rows. A shard holds only the rows
+	// assigned to a single validator, which never exceeds MaxRowsPerValidator
+	// (4096 for the default v0 parameters).
+	MaxBlobRowsPerShard = 4096
+
+	// MaxProofSegmentsPerRow bounds BlobRow.Proof. A row's Merkle inclusion proof
+	// has ceil(log2(TotalRows)) segments (14 for the default v0 parameters, where
+	// TotalRows is 16384).
+	MaxProofSegmentsPerRow = 14
+)
```
