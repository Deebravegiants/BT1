# [?] op-batcher: prevent `SpanChannelOut` RLP bytes overflowing `MaxRLPBytesPerChannel` (#14310)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2025-02-14
Source: https://github.com/bobanetwork/boba/commit/dcce927ab82ca3977ca1ecc5ad03ea7dd851a57e
Type: security-commit

## Details
op-batcher: prevent `SpanChannelOut` RLP bytes overflowing `MaxRLPBytesPerChannel` (#14310)

* fix op-batcher pack over MaxRLPBytesChannel

* add test cases from different CompressionAlgo

* add fresh compression logic and corresponding comments

* refactor: enhance MaxRLPBytesPerChannel test

* refactor: rename variable and add required messages

## Patch
### op-node/rollup/derive/channel_out_test.go
```diff
@@ -491,3 +491,27 @@ func testSpanChannelOut_MaxBlocksPerSpanBatch(t *testing.T, tt maxBlocksTest) {
 		require.Equalf(t, batch0, batch, "iteration %d", i)
 	}
 }
+
+func TestSpanChannelOut_MaxRLPBytesPerChannel(t *testing.T) {
+	for _, algo := range CompressionAlgos {
+		t.Run("testSpanChannelOut_MaxRLPBytesPerChannel_"+algo.String(), func(t *testing.T) {
+			testSpanChannelOut_MaxRLPBytesPerChannel(t, algo)
+		})
+	}
+}
+
+func testSpanChannelOut_MaxRLPBytesPerChannel(t *testing.T, algo CompressionAlgo) {
+
+	maxRLPBytesPerChannel := int(rollup.NewChainSpec(&rollupCfg).MaxRLPBytesPerChannel(0))
+	cout, singularBatches := SpanChannelAndBatches(t, 100, 1, algo)
+
+	cout.rlp[0] = bytes.NewBuffer(make([]byte, maxRLPBytesPerChannel))
+	cout.rlp[1] = bytes.NewBuffer(make([]byte, maxRLPBytesPerChannel))
+	cout.sealedRLPBytes = maxRLPBytesPerChannel
+
+	err := cout.addSingularBatch(singularBatches[0], 1)
+	require.ErrorIs(t, err, ErrTooManyRLPBytes, "error should be ErrTooManyRLPBytes")
+
+	require.Equal(t, cout.activeRLP().Len(), maxRLPBytesPerChannel, "active RLP should be equal to the max RLP limit")
+	require.Greater(t, cout.inactiveRLP().Len(), maxRLPBytesPerChannel, "inactive RLP should be greater than max RLP limit")
+}
```

### op-node/rollup/derive/span_channel_out.go
```diff
@@ -178,6 +178,13 @@ func (co *SpanChannelOut) addSingularBatch(batch *SingularBatch, seqNum uint64)
 	// the Fjord activation.
 	maxRLPBytesPerChannel := co.chainSpec.MaxRLPBytesPerChannel(batch.Timestamp)
 	if active.Len() > int(maxRLPBytesPerChannel) {
+
+		// if active size exceeds MaxRLPBytesPerChannel we revert the last batch
+		// by switching the RLP buffer and doing a fresh compression
+		co.swapRLP()
+		if err = co.compress(); err != nil {
+			return err
+		}
 		return fmt.Errorf("could not take %d bytes as replacement of channel of %d bytes, max is %d. err: %w",
 			active.Len(), co.inactiveRLP().Len(), maxRLPBytesPerChannel, ErrTooManyRLPBytes)
 	}
```
