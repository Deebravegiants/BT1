# [?] rpcdaemon: fix to avoid panic()  on receipts log index when ASSERT_ERIGON is enabled (#16908)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-09-01
Source: https://github.com/erigontech/erigon/commit/02bf5dc30abd4325586241ed7fa5f44f3fa321a8
Type: security-commit

## Details
rpcdaemon: fix to avoid panic()  on receipts log index when ASSERT_ERIGON is enabled (#16908)

Assign correctly the receipt.FirstLogIndexWithinBlock when the receipt
contains zero logs to avoid panic() if ASSERT_ERIGON is enabled

## Patch
### rpc/jsonrpc/receipts/receipts_generator.go
```diff
@@ -339,10 +339,12 @@ func (g *Generator) GetReceipts(ctx context.Context, cfg *chain.Config, tx kv.Te
 		receipt.BlockHash = blockHash
 		if len(receipt.Logs) > 0 {
 			receipt.FirstLogIndexWithinBlock = uint32(receipt.Logs[0].Index)
+		} else if i > 0 {
+			receipt.FirstLogIndexWithinBlock = receipts[i-1].FirstLogIndexWithinBlock + uint32(len(receipts[i-1].Logs))
 		}
 		receipts[i] = receipt
 
-		if dbg.AssertEnabled && receiptsFromDB != nil && len(receipts) > 0 {
+		if dbg.AssertEnabled && receiptsFromDB != nil {
 			g.assertEqualReceipts(receipt, receiptsFromDB[i])
 		}
 	}
```
