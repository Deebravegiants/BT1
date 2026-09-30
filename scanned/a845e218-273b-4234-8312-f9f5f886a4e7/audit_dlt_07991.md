# [?] Fix panic on getting safe block

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2024-10-08
Source: https://github.com/0xPolygon/bor/commit/a7578a3ceab74b0551b115dd1a3250d7e870a329
Type: security-commit

## Details
Fix panic on getting safe block

Since bor doesn't have "safe" block, the api should always return null when requested safe block.

## Patch
### eth/api_backend.go
```diff
@@ -157,7 +157,11 @@ func (b *EthAPIBackend) BlockByNumber(ctx context.Context, number rpc.BlockNumbe
 	if number == rpc.SafeBlockNumber {
 		header := b.eth.blockchain.CurrentSafeBlock()
 
-		return b.eth.blockchain.GetBlock(header.Hash(), header.Number.Uint64()), nil
+		if header == nil {
+			return nil, errors.New("safe block not found")
+		} else {
+			return b.eth.blockchain.GetBlock(header.Hash(), header.Number.Uint64()), nil
+		}
 	}
 
 	return b.eth.blockchain.GetBlockByNumber(uint64(number)), nil
```

### internal/ethapi/api_test.go
```diff
@@ -1818,6 +1818,11 @@ func TestRPCGetBlockOrHeader(t *testing.T) {
 			fullTx:    true,
 			file:      "hash-pending-fullTx",
 		},
+		// 26. safe block
+		{
+			blockNumber: rpc.SafeBlockNumber,
+			file:        "tag-safe",
+		},
 	}
 
 	for i, tt := range testSuite {
```

### internal/ethapi/testdata/eth_getBlockByNumber-tag-safe.json
```diff
@@ -0,0 +1 @@
+null
\ No newline at end of file
```
