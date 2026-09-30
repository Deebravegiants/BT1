# [?] internal/ethapi: fix panic in debug methods (#31157)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-02-11
Source: https://github.com/ethereum/go-ethereum/commit/da71839a270a353bac92e3108e4b74fb0eefec29
Type: security-commit

## Details
internal/ethapi: fix panic in debug methods (#31157)

Fixes an error when the block is not found in debug methods.

## Patch
### internal/ethapi/api.go
```diff
@@ -1675,7 +1675,7 @@ func (api *DebugAPI) GetRawHeader(ctx context.Context, blockNrOrHash rpc.BlockNu
 		hash = h
 	} else {
 		block, err := api.b.BlockByNumberOrHash(ctx, blockNrOrHash)
-		if err != nil {
+		if block == nil || err != nil {
 			return nil, err
 		}
 		hash = block.Hash()
@@ -1694,7 +1694,7 @@ func (api *DebugAPI) GetRawBlock(ctx context.Context, blockNrOrHash rpc.BlockNum
 		hash = h
 	} else {
 		block, err := api.b.BlockByNumberOrHash(ctx, blockNrOrHash)
-		if err != nil {
+		if block == nil || err != nil {
 			return nil, err
 		}
 		hash = block.Hash()
@@ -1713,7 +1713,7 @@ func (api *DebugAPI) GetRawReceipts(ctx context.Context, blockNrOrHash rpc.Block
 		hash = h
 	} else {
 		block, err := api.b.BlockByNumberOrHash(ctx, blockNrOrHash)
-		if err != nil {
+		if block == nil || err != nil {
 			return nil, err
 		}
 		hash = block.Hash()
```
