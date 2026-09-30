# [?] fix nil deref when checking for ReplacementNotAllowed error

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-05-20
Source: https://github.com/OffchainLabs/nitro/commit/9dc810b3e0ab8ab6fd4cde1047aa42e10f7e4aaf
Type: security-commit

## Details
fix nil deref when checking for ReplacementNotAllowed error

## Patch
### arbnode/dataposter/data_poster.go
```diff
@@ -950,8 +950,8 @@ func (p *DataPoster) sendTx(ctx context.Context, prevTx *storage.QueuedTransacti
 		isAlreadyKnown = isAlreadyKnown || strings.Contains(err.Error(), "nonce too low")
 		// If we previously sent this nonce and the same tx, some L1 clients may return ReplacementNotAllowed instead of
 		// an already known error (might be due to their cache size constraints) so we dont return an error in such a case
-		_, _, err := p.client.TransactionByHash(ctx, newTx.FullTx.Hash())
-		isAlreadyKnown = isAlreadyKnown || (strings.Contains(err.Error(), "ReplacementNotAllowed") && err == nil)
+		_, _, errTxByHash := p.client.TransactionByHash(ctx, newTx.FullTx.Hash())
+		isAlreadyKnown = isAlreadyKnown || (strings.Contains(err.Error(), "ReplacementNotAllowed") && errTxByHash == nil)
 		if !isAlreadyKnown {
 			log.Warn("DataPoster failed to send transaction", "err", err, "nonce", newTx.FullTx.Nonce(), "feeCap", newTx.FullTx.GasFeeCap(), "tipCap", newTx.FullTx.GasTipCap(), "blobFeeCap", newTx.FullTx.BlobGasFeeCap(), "gas", newTx.FullTx.Gas())
 			return err
```
