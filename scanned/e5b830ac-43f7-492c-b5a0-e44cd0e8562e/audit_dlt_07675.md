# [?] Fixed data race in bor seal function (#14755)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-04-25
Source: https://github.com/erigontech/erigon/commit/daa5419828c10aa24891ac4f141595ee6f53d6e9
Type: security-commit

## Details
Fixed data race in bor seal function (#14755)

## Patch
### polygon/bor/bor.go
```diff
@@ -1166,7 +1166,7 @@ func (c *Bor) Authorize(currentSigner common.Address, signFn SignerFn) {
 func (c *Bor) Seal(chain consensus.ChainHeaderReader, blockWithReceipts *types.BlockWithReceipts, results chan<- *types.BlockWithReceipts, stop <-chan struct{}) error {
 	block := blockWithReceipts.Block
 	receipts := blockWithReceipts.Receipts
-	header := block.HeaderNoCopy()
+	header := block.Header()
 	// Sealing the genesis block is not supported
 	number := header.Number.Uint64()
 
```
