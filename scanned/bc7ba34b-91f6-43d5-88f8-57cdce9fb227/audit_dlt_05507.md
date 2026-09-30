# [?] Reject lamport underflow in event parent deserialization (#981)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2026-05-20
Source: https://github.com/0xsoniclabs/sonic/commit/33877f981af65949675d01773d4b89dcb189e34b
Type: security-commit

## Details
Reject lamport underflow in event parent deserialization (#981)

A peer-controlled lamportDiff exceeding the event's own lamport causes a silent uint32 underflow,
producing a garbage parent ID that stalls in the DAG buffer indefinitely without triggering a peer ban.
Reject such events with ErrMalformedEncoding instead.

## Patch
### inter/event_serializer.go
```diff
@@ -144,6 +144,9 @@ func eventUnmarshalCSER(r *cser.Reader, e *MutableEventPayload) (err error) {
 	for i := uint32(0); i < parentsNum; i++ {
 		// lamport difference
 		lamportDiff := r.U32()
+		if lamportDiff > lamport {
+			return cser.ErrMalformedEncoding
+		}
 		// hash
 		h := [24]byte{}
 		r.FixedBytes(h[:])
```

### inter/event_serializer_test.go
```diff
@@ -242,6 +242,50 @@ func TestEventUnmarshalCSER_Version3DetectsUnsupportedPayload(t *testing.T) {
 	}
 }
 
+// TestEventUnmarshalCSER_RejectsLamportUnderflow encodes an event
+// where a parent's lamportDiff exceeds the event's own lamport,
+// which would cause a silent uint32 underflow when reconstructing the parent ID.
+func TestEventUnmarshalCSER_RejectsLamportUnderflow(t *testing.T) {
+	const (
+		eventLamport = uint32(5)
+		lamportDiff  = uint32(10) // greater than eventLamport
+	)
+
+	// encoding such invalid event not allowed by regular EventPayload marshaller
+	encoded, err := cser.MarshalBinaryAdapter(func(w *cser.Writer) error {
+		w.BitsW.Write(2, 0)
+		w.U8(2) // version 2
+		// header
+		w.U16(0)             // netForkID
+		w.U32(1)             // epoch
+		w.U32(eventLamport)  // lamport
+		w.U32(1)             // creator
+		w.U32(1)             // seq
+		w.U32(0)             // frame
+		w.U64(1_000_000_000) // creationTime
+		w.I64(0)             // medianTimeDiff
+		w.U64(0)             // gasPowerUsed
+		w.U64(0)             // gasPowerLeft[0]
+		w.U64(0)             // gasPowerLeft[1]
+		// one parent whose diff exceeds the event's own lamport
+		w.U32(1) // parentsNum
+		w.U32(lamportDiff)
+		w.FixedBytes(make([]byte, 24)) // parent ID hash suffix
+		// remaining fields
+		w.Bool(false)                  // prevEpochHash absent
+		w.Bool(false)                  // anyTxs
+		w.SliceBytes([]byte{})         // extra
+		w.FixedBytes(make([]byte, 64)) // signature (read by UnmarshalCSER after eventUnmarshalCSER)
+		return nil
+	})
+	require.NoError(t, err)
+
+	var decoded EventPayload
+	err = decoded.UnmarshalBinary(encoded)
+	require.ErrorIs(t, err, cser.ErrMalformedEncoding,
+		"lamportDiff > lamport must be rejected, not silently accepted as a garbage parent ID")
+}
+
 func TestEventPayloadMarshalCSER_DetectsInvalidTransactionEncoding(t *testing.T) {
 	require := require.New(t)
 
```
