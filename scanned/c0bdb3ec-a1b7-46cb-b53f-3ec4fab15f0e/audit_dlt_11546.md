# [?] Fix: index of bounds panics (#417)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2024-03-31
Source: https://github.com/Layr-Labs/eigenda/commit/4c28f5894a99f0e66a65b8e73c10adcac5cbf956
Type: security-commit

## Details
Fix: index of bounds panics (#417)

## Patch
### core/aggregation.go
```diff
@@ -78,9 +78,12 @@ func NewStdSignatureAggregator(logger logging.Logger, transactor Transactor) (*S
 var _ SignatureAggregator = (*StdSignatureAggregator)(nil)
 
 func (a *StdSignatureAggregator) AggregateSignatures(ctx context.Context, state *IndexedOperatorState, quorumIDs []QuorumID, message [32]byte, messageChan chan SignerMessage) (*SignatureAggregation, error) {
-
 	// TODO: Add logging
 
+	if len(quorumIDs) == 0 {
+		return nil, errors.New("the number of quorums must be greater than zero")
+	}
+
 	// Ensure all quorums are found in state
 	for _, id := range quorumIDs {
 		_, found := state.Operators[id]
```

### encoding/kzg/verifier/batch_commit_equivalence.go
```diff
@@ -30,6 +30,9 @@ func GetRandomFr() (fr.Element, error) {
 }
 
 func CreateRandomnessVector(n int) ([]fr.Element, error) {
+	if n <= 0 {
+		return nil, errors.New("the length of vector must be positive")
+	}
 	r, err := GetRandomFr()
 	if err != nil {
 		return nil, err
```

### encoding/kzg/verifier/multiframe.go
```diff
@@ -186,6 +186,9 @@ func (v *Verifier) UniversalVerify(params encoding.EncodingParams, samples []Sam
 
 	n := len(samples)
 	fmt.Printf("Batch verify %v frames of %v symbols out of %v blobs \n", n, params.ChunkLength, m)
+	if n == 0 {
+		return errors.New("the number of samples (i.e. chunks) must not be empty")
+	}
 
 	// generate random field elements to aggregate equality check
 	randomsFr, err := CreateRandomnessVector(n)
```

### node/node.go
```diff
@@ -267,6 +267,13 @@ func (n *Node) ProcessBatch(ctx context.Context, header *core.BatchHeader, blobs
 
 	log.Debug("Processing batch", "num of blobs", len(blobs))
 
+	if len(blobs) == 0 {
+		return nil, errors.New("the number of blobs must be greater than zero")
+	}
+	if len(blobs) != len(rawBlobs) {
+		return nil, errors.New("the number of parsed blobs must be the same as number of blobs from protobuf request")
+	}
+
 	// Measure num batches received and its size in bytes
 	batchSize := int64(0)
 	for _, blob := range blobs {
```
