# [?] Fixed false positive data race. (#18479)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-12-26
Source: https://github.com/erigontech/erigon/commit/24035b43e8f3d28ff33c60f87ba4b21c174f2ef1
Type: security-commit

## Details
Fixed false positive data race. (#18479)

Race detector does not like the setter before goroutine start for some
reason. so don't use DB directly from the struct.

---------

Co-authored-by: Giulio <monkeair@MacBook-Air-di-Giulio.local>

## Patch
### execution/commitment/commitmentdb/commitment_context.go
```diff
@@ -307,18 +307,22 @@ func (sdc *SharedDomainsCommitmentContext) ComputeCommitment(ctx context.Context
 
 	var warmupConfig commitment.WarmupConfig
 	if sdc.warmupDB != nil {
+		// avoid races like this
+		db := sdc.warmupDB
+		txNum := sdc.sharedDomains.TxNum()
+		stepSize := sdc.sharedDomains.StepSize()
 		// Create factory for warmup TrieContexts with their own transactions
 		ctxFactory := func() (commitment.PatriciaContext, func()) {
-			roTx, err := sdc.warmupDB.BeginTemporalRo(ctx) //nolint:gocritic
+			roTx, err := db.BeginTemporalRo(ctx) //nolint:gocritic
 			if err != nil {
 				return &errorTrieContext{err: err}, nil
 			}
 
 			warmupCtx := &TrieContext{
 				roTtx:    roTx,
 				getter:   sdc.sharedDomains.AsGetter(roTx),
-				stepSize: sdc.sharedDomains.StepSize(),
-				txNum:    sdc.sharedDomains.TxNum(),
+				stepSize: stepSize,
+				txNum:    txNum,
 			}
 			if sdc.stateReader != nil {
 				warmupCtx.stateReader = sdc.stateReader
```
