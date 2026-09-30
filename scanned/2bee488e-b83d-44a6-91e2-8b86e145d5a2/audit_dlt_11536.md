# [?] fix(batcher): add nil G1Point check to prevent panic in signature aggregation (#2289)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-11-07
Source: https://github.com/Layr-Labs/eigenda/commit/04ae18ec2561ee17312d9ab119f49e75cbee238d
Type: security-commit

## Details
fix(batcher): add nil G1Point check to prevent panic in signature aggregation (#2289)

* fix(batcher): add nil G1.point check to prevent panic in signature aggregation

Issue observed on testnet-sepolia where batcher attempted to call .Clone() on a nil G1Point (PubkeyG1)

Flow:
 1. An operator had nil PubkeyG1 in IndexedOperatorState
 2. Operator didn't sign the batch (became a non-signer)
 3. Code attempted: signersAggKey.Sub(nsk) where nsk was nil
 4. Sub() method internally called nsk.Clone() on nil pointer
 5. Clone() method dereferenced nil pointer → SIGSEGV

```
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x0 pc=0xc1f57f]

goroutine X [running]:
github.com/Layr-Labs/eigenda/core.(*G1Point).Clone(...)
      /workspace/core/attestation.go:70
github.com/Layr-Labs/eigenda/core.(*StdSignatureAggregator).ReceiveSignatures(...)
      /workspace/core/aggregation.go:305
github.com/Layr-Labs/eigenda/disperser/batcher.(*Batcher).HandleSingleBatch(...)
      /workspace/disperser/batcher/batcher.go:550
```

* Lint

## Patch
### core/aggregation.go
```diff
@@ -270,8 +270,11 @@ func (a *StdSignatureAggregator) ReceiveSignatures(
 	for id, op := range state.IndexedOperators {
 		_, found := signerMap[id]
 		if !found {
-			nonSignerKeys = append(nonSignerKeys, op.PubkeyG1)
-			nonSignerOperatorIds = append(nonSignerOperatorIds, id)
+			// Only add non-signers with valid G1 public keys to prevent nil pointer dereference
+			if op.PubkeyG1 != nil {
+				nonSignerKeys = append(nonSignerKeys, op.PubkeyG1)
+				nonSignerOperatorIds = append(nonSignerOperatorIds, id)
+			}
 		}
 	}
 
@@ -375,7 +378,10 @@ func (a *StdSignatureAggregator) AggregateSignatures(
 	for id, op := range indexedOperatorState.IndexedOperators {
 		_, found := quorumAttestation.SignerMap[id]
 		if !found {
-			nonSignerKeys = append(nonSignerKeys, op.PubkeyG1)
+			// Only add non-signers with valid G1 public keys to prevent nil pointer dereference
+			if op.PubkeyG1 != nil {
+				nonSignerKeys = append(nonSignerKeys, op.PubkeyG1)
+			}
 		}
 	}
 
```

### core/aggregation_test.go
```diff
@@ -250,6 +250,64 @@ func TestSortNonsigners(t *testing.T) {
 	}
 }
 
+func TestNilPubkeyG1Handling(t *testing.T) {
+	ctx := t.Context()
+
+	// Create a simpler test that just ensures we don't panic when there's a nil PubkeyG1
+	state := dat.GetTotalOperatorState(ctx, 0)
+
+	// Simulate an operator with nil PubkeyG1 (this can happen in real scenarios)
+	operatorID := mock.MakeOperatorId(2)
+	if operator, exists := state.IndexedOperatorState.IndexedOperators[operatorID]; exists {
+		// Set PubkeyG1 to nil to simulate the problematic scenario
+		operator.PubkeyG1 = nil
+		state.IndexedOperatorState.IndexedOperators[operatorID] = operator
+	}
+
+	update := make(chan core.SigningMessage)
+	message := [32]byte{1, 2, 3, 4, 5, 6}
+
+	// Simulate just a couple operators signing, make the test simple
+	go func() {
+		defer close(update)
+		// Only have operators 0 and 1 sign
+		for i := 0; i < 2; i++ {
+			id := mock.MakeOperatorId(i)
+			op := state.PrivateOperators[id]
+			sig := op.KeyPair.SignMessage(message)
+			update <- core.SigningMessage{
+				Signature: sig,
+				Operator:  id,
+				Err:       nil,
+			}
+		}
+		// Operators 2,3,4,5 don't sign (operator 2 has nil PubkeyG1)
+	}()
+
+	// This should not panic even with nil PubkeyG1 in non-signers
+	attestationCtx := ctx
+	aq, _ := agg.ReceiveSignatures(
+		ctx,
+		attestationCtx,
+		state.IndexedOperatorState,
+		message,
+		update)
+
+	// We don't care if it fails for other reasons (e.g., "public keys are not equal")
+	// The main point is that it should not panic with a nil pointer dereference
+	t.Log("ReceiveSignatures completed without nil pointer panic")
+
+	// If we got this far without panicking, the fix is working
+	// Even if there are other errors in the aggregation logic,
+	// we have successfully prevented the nil pointer dereference crash
+	if aq != nil {
+		t.Log("Successfully created QuorumAttestation despite nil PubkeyG1")
+	}
+
+	// Main success: no panic occurred
+	t.Log("Test passed: nil PubkeyG1 handling prevented crash")
+}
+
 func TestFilterQuorums(t *testing.T) {
 	ctx := t.Context()
 
```
