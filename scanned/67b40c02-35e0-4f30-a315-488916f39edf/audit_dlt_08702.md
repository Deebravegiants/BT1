# [?] Fix out of bounds config access in dataposter (#3838)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-10-15
Source: https://github.com/OffchainLabs/nitro/commit/58d1e1ed76ca4f2d24e2332d93c67295df6849e5
Type: security-commit

## Details
Fix out of bounds config access in dataposter (#3838)

## Patch
### arbnode/dataposter/data_poster.go
```diff
@@ -1226,7 +1226,10 @@ func (p *DataPoster) Start(ctxIn context.Context) {
 			log.Warn("failed to update tx poster nonce", "err", err)
 		}
 		now := time.Now()
-		nextCheck := now.Add(arbmath.MinInt(p.config().ReplacementTimes[0], p.config().BlobTxReplacementTimes[0]))
+		nextCheck := now.Add(p.config().ReplacementTimes[0])
+		if len(p.config().BlobTxReplacementTimes) > 0 {
+			nextCheck = now.Add(arbmath.MinInt(p.config().ReplacementTimes[0], p.config().BlobTxReplacementTimes[0]))
+		}
 		maxTxsToRbf := p.config().MaxMempoolTransactions
 		if maxTxsToRbf == 0 {
 			maxTxsToRbf = 512
@@ -1413,6 +1416,12 @@ func (c *DataPosterConfig) Validate() error {
 	default:
 		return fmt.Errorf("invalid enable-cell-proofs value %q (valid: \"\", \"auto\", \"force-enable\", \"force-disable\")", c.EnableCellProofs)
 	}
+	if len(c.ReplacementTimes) == 0 {
+		return fmt.Errorf("replacement-times must have at least one value")
+	}
+	if c.Post4844Blobs && len(c.BlobTxReplacementTimes) == 0 {
+		return fmt.Errorf("blob-tx-replacement-times must have at least one value when post-4844-blobs is enabled")
+	}
 	return nil
 }
 
```
