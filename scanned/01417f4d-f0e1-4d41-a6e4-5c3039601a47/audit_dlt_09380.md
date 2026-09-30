# [?] fix(blockchain): remove reachable panic in blobsidecar processing (#2244)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-12-11
Source: https://github.com/berachain/beacon-kit/commit/36f1a040d5adf9c8cfe188fdd9ee087aab2c9633
Type: security-commit

## Details
fix(blockchain): remove reachable panic in blobsidecar processing (#2244)

## Patch
### consensus-types/types/body.go
```diff
@@ -73,12 +73,12 @@ func (b *BeaconBlockBody) Empty(forkVersion uint32) *BeaconBlockBody {
 func BlockBodyKZGOffset(
 	slot math.Slot,
 	cs common.ChainSpec,
-) uint64 {
+) (uint64, error) {
 	switch cs.ActiveForkVersionForSlot(slot) {
 	case version.Deneb:
-		return KZGMerkleIndexDeneb * cs.MaxBlobCommitmentsPerBlock()
+		return KZGMerkleIndexDeneb * cs.MaxBlobCommitmentsPerBlock(), nil
 	default:
-		panic(ErrForkVersionNotSupported)
+		return 0, ErrForkVersionNotSupported
 	}
 }
 
```

### da/blob/processor.go
```diff
@@ -49,7 +49,7 @@ type Processor[
 	verifier *verifier[BeaconBlockHeaderT, BlobSidecarT, BlobSidecarsT]
 	// blockBodyOffsetFn is a function that calculates the block body offset
 	// based on the slot and chain specifications.
-	blockBodyOffsetFn func(math.Slot, common.ChainSpec) uint64
+	blockBodyOffsetFn func(math.Slot, common.ChainSpec) (uint64, error)
 	// metrics is used to collect and report processor metrics.
 	metrics *processorMetrics
 }
@@ -68,7 +68,7 @@ func NewProcessor[
 	logger log.Logger,
 	chainSpec common.ChainSpec,
 	proofVerifier kzg.BlobProofVerifier,
-	blockBodyOffsetFn func(math.Slot, common.ChainSpec) uint64,
+	blockBodyOffsetFn func(math.Slot, common.ChainSpec) (uint64, error),
 	telemetrySink TelemetrySink,
 ) *Processor[
 	AvailabilityStoreT, BeaconBlockBodyT, BeaconBlockHeaderT,
@@ -110,14 +110,16 @@ func (sp *Processor[
 		return nil
 	}
 
+	kzgOffset, err := sp.blockBodyOffsetFn(
+		blkHeader.GetSlot(), sp.chainSpec,
+	)
+	if err != nil {
+		return err
+	}
+
 	// Verify the blobs and ensure they match the local state.
 	return sp.verifier.verifySidecars(
-		sidecars,
-		sp.blockBodyOffsetFn(
-			sidecars.Get(0).GetBeaconBlockHeader().GetSlot(),
-			sp.chainSpec,
-		),
-		blkHeader,
+		sidecars, kzgOffset, blkHeader,
 	)
 }
 
```
