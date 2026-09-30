# [?] Check if block is nil to prevent panic (#736)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2023-02-10
Source: https://github.com/0xPolygon/bor/commit/0ed78b9261b377653e0e201b3e5986903e3fd94e
Type: security-commit

## Details
Check if block is nil to prevent panic (#736)

## Patch
### internal/ethapi/api.go
```diff
@@ -628,6 +628,10 @@ func (s *PublicBlockChainAPI) GetTransactionReceiptsByBlock(ctx context.Context,
 		return nil, err
 	}
 
+	if block == nil {
+		return nil, errors.New("block not found")
+	}
+
 	receipts, err := s.b.GetReceipts(ctx, block.Hash())
 	if err != nil {
 		return nil, err
```
