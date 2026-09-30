# [?] fix(batcher): Handle nil dereference in signature aggregation due to subgraph failure (#2428)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-12-19
Source: https://github.com/Layr-Labs/eigenda/commit/202235d8701fa680507c8ac9ae8c686ea081f3c7
Type: security-commit

## Details
fix(batcher): Handle nil dereference in signature aggregation due to subgraph failure (#2428)

* Handle nil dereference in signature aggregation due to subgraph failure

* fail fast return error

## Patch
### core/aggregation.go
```diff
@@ -303,6 +303,9 @@ func (a *StdSignatureAggregator) ReceiveSignatures(
 		// Verify that the aggregated public key for the quorum matches the on-chain quorum aggregate public key
 		// sans non-signers of the quorum
 		quorumAggKey := state.AggKeys[quorumID]
+		if quorumAggKey == nil {
+			return nil, fmt.Errorf("no aggregate public key found for quorum %d", quorumID)
+		}
 		quorumAggPubKeys[quorumID] = quorumAggKey
 
 		signersAggKey := quorumAggKey.Clone()
```

### core/aggregation_test.go
```diff
@@ -308,6 +308,37 @@ func TestNilPubkeyG1Handling(t *testing.T) {
 	t.Log("Test passed: nil PubkeyG1 handling prevented crash")
 }
 
+// TestNilAggKeyHandling tests that ReceiveSignatures returns an error when aggregate public keys
+// are nil. This simulates the scenario where TheGraph API fails to return aggregate
+// public keys for a quorum (e.g., due to network issues or missing data).
+func TestNilAggKeyHandling(t *testing.T) {
+	ctx := t.Context()
+
+	state := dat.GetTotalOperatorStateWithQuorums(ctx, 0, []core.QuorumID{0, 1})
+
+	// Simulate TheGraph API failure by setting AggKeys to nil for quorum 0
+	state.IndexedOperatorState.AggKeys[0] = nil
+
+	update := make(chan core.SigningMessage)
+	message := [32]byte{1, 2, 3, 4, 5, 6}
+
+	// Have all operators sign successfully
+	go simulateOperators(*state, message, update, 0)
+
+	// This should return an error for nil AggKeys
+	aq, err := agg.ReceiveSignatures(
+		ctx,
+		ctx,
+		state.IndexedOperatorState,
+		message,
+		update)
+
+	// The function should return an error indicating the missing aggregate key
+	assert.Error(t, err)
+	assert.Nil(t, aq)
+	assert.Contains(t, err.Error(), "no aggregate public key found for quorum 0")
+}
+
 func TestFilterQuorums(t *testing.T) {
 	ctx := t.Context()
 
```
