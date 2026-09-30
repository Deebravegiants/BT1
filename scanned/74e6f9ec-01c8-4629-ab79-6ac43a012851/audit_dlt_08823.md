# [?] fix(taiko-client): resolve race condition in TryAggregate (#20924)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2025-12-15
Source: https://github.com/taikoxyz/taiko-mono/commit/d92045da23daf8a5faff054168d6606f59922fa6
Type: security-commit

## Details
fix(taiko-client): resolve race condition in TryAggregate (#20924)

Co-authored-by: David <david@taiko.xyz>

## Patch
### packages/taiko-client/prover/proof_producer/proof_buffer.go
```diff
@@ -113,18 +113,23 @@ func (pb *ProofBuffer) ClearItems(blockIDs ...uint64) int {
 	}
 
 	pb.buffer = newBuffer
-	pb.isAggregating = false
 	if len(pb.buffer) == 0 {
 		pb.firstItemAt = time.Time{}
 	}
+	pb.isAggregating = false
 	return clearedCount
 }
 
-// MarkAggregating marks the proofs in this buffer are aggregating.
-func (pb *ProofBuffer) MarkAggregating() {
+// MarkAggregatingIfNot marks the proofs in this buffer are aggregating if not.
+func (pb *ProofBuffer) MarkAggregatingIfNot() bool {
 	pb.mutex.Lock()
 	defer pb.mutex.Unlock()
+
+	if pb.isAggregating {
+		return false
+	}
 	pb.isAggregating = true
+	return true
 }
 
 // IsAggregating returns if the proofs in this buffer are aggregating.
```

### packages/taiko-client/prover/proof_producer/proof_buffer_test.go
```diff
@@ -24,7 +24,7 @@ func TestProofBuffer(t *testing.T) {
 	}
 
 	// Mark its aggregating status.
-	b.MarkAggregating()
+	b.MarkAggregatingIfNot()
 	require.True(t, b.IsAggregating())
 
 	// Clear items from the buffer.
```

### packages/taiko-client/prover/proof_submitter/proof_submitter.go
```diff
@@ -269,15 +269,16 @@ func (s *ProofSubmitterPacaya) RequestProof(ctx context.Context, meta metadata.T
 // TryAggregate tries to aggregate the proofs in the buffer, if the buffer is full,
 // or the forced aggregation interval has passed.
 func (s *ProofSubmitterPacaya) TryAggregate(buffer *proofProducer.ProofBuffer, proofType proofProducer.ProofType) bool {
-	if !buffer.IsAggregating() &&
-		(uint64(buffer.Len()) >= buffer.MaxLength ||
-			(buffer.Len() != 0 && time.Since(buffer.FirstItemAt()) > s.forceBatchProvingInterval)) {
-		buffer.MarkAggregating()
-		s.batchAggregationNotify <- proofType
+	// Check conditions first (without locking)
+	if uint64(buffer.Len()) < buffer.MaxLength &&
+		(buffer.Len() == 0 || time.Since(buffer.FirstItemAt()) <= s.forceBatchProvingInterval) {
+		return false
+	}
 
+	if buffer.MarkAggregatingIfNot() { // Returns true if successfully marked
+		s.batchAggregationNotify <- proofType
 		return true
 	}
-
 	return false
 }
 
@@ -408,6 +409,14 @@ func (s *ProofSubmitterPacaya) AggregateProofsByType(ctx context.Context, proofT
 		backoff.WithContext(backoff.NewConstantBackOff(s.proofPollingInterval), ctx),
 	); err != nil {
 		log.Error("Aggregate proof error", "error", err)
+		batchIDs := make([]uint64, 0, len(buffer))
+		for _, proof := range buffer {
+			if proof.BatchID == nil {
+				continue
+			}
+			batchIDs = append(batchIDs, proof.BatchID.Uint64())
+		}
+		proofBuffer.ClearItems(batchIDs...)
 		return err
 	}
 	return nil
```

### packages/taiko-client/prover/proof_submitter/proof_submitter_shasta.go
```diff
@@ -333,10 +333,13 @@ func (s *ProofSubmitterShasta) BatchSubmitProofs(ctx context.Context, batchProof
 // TryAggregate tries to aggregate the proofs in the buffer, if the buffer is full,
 // or the forced aggregation interval has passed.
 func (s *ProofSubmitterShasta) TryAggregate(buffer *proofProducer.ProofBuffer, proofType proofProducer.ProofType) bool {
-	if !buffer.IsAggregating() &&
-		(uint64(buffer.Len()) >= buffer.MaxLength ||
-			(buffer.Len() != 0 && time.Since(buffer.FirstItemAt()) > s.forceBatchProvingInterval)) {
-		buffer.MarkAggregating()
+	// Check conditions first (without locking)
+	if uint64(buffer.Len()) < buffer.MaxLength &&
+		(buffer.Len() == 0 || time.Since(buffer.FirstItemAt()) <= s.forceBatchProvingInterval) {
+		return false
+	}
+
+	if buffer.MarkAggregatingIfNot() { // Returns true if successfully marked
 		s.batchAggregationNotify <- proofType
 		return true
 	}
@@ -394,6 +397,14 @@ func (s *ProofSubmitterShasta) AggregateProofsByType(ctx context.Context, proofT
 		backoff.WithContext(backoff.NewConstantBackOff(s.proofPollingInterval), ctx),
 	); err != nil {
 		log.Error("Aggregate proof error", "error", err)
+		batchIDs := make([]uint64, 0, len(buffer))
+		for _, proof := range buffer {
+			if proof.BatchID == nil {
+				continue
+			}
+			batchIDs = append(batchIDs, proof.BatchID.Uint64())
+		}
+		proofBuffer.ClearItems(batchIDs...)
 		return err
 	}
 	return nil
```
