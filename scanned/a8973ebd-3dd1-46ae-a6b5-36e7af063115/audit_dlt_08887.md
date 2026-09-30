# [?] Fix potential nil pointer dereference

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2023-09-22
Source: https://github.com/NethermindEth/juno/commit/d3fd4cc7161b4bde88bcbea7b063e0d22d7954b0
Type: security-commit

## Details
Fix potential nil pointer dereference

## Patch
### rpc/handlers.go
```diff
@@ -153,8 +153,10 @@ func (h *Handler) BlockWithTxHashes(id BlockID) (*BlockWithTxHashes, *jsonrpc.Er
 
 func (h *Handler) LegacyBlockWithTxHashes(id BlockID) (*BlockWithTxHashes, *jsonrpc.Error) {
 	block, err := h.BlockWithTxHashes(id)
-	block.BlockHeader.L1GasPrice = nil
-	block.BlockHeader.StarknetVersion = ""
+	if block != nil {
+		block.BlockHeader.L1GasPrice = nil
+		block.BlockHeader.StarknetVersion = ""
+	}
 	return block, err
 }
 
@@ -236,8 +238,10 @@ func (h *Handler) BlockWithTxs(id BlockID) (*BlockWithTxs, *jsonrpc.Error) {
 
 func (h *Handler) LegacyBlockWithTxs(id BlockID) (*BlockWithTxs, *jsonrpc.Error) {
 	block, err := h.BlockWithTxs(id)
-	block.BlockHeader.L1GasPrice = nil
-	block.BlockHeader.StarknetVersion = ""
+	if block != nil {
+		block.BlockHeader.L1GasPrice = nil
+		block.BlockHeader.StarknetVersion = ""
+	}
 	return block, err
 }
 
```
