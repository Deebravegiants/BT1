# [?] internal/ethapi: avoid int overflow in GetTransactionReceipt (#26911)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-03-16
Source: https://github.com/ethereum/go-ethereum/commit/f73365738309d9b3249efca9c1492856bf6e7848
Type: security-commit

## Details
internal/ethapi: avoid int overflow in GetTransactionReceipt (#26911)

## Patch
### internal/ethapi/api.go
```diff
@@ -1626,7 +1626,7 @@ func (s *TransactionAPI) GetTransactionReceipt(ctx context.Context, hash common.
 	if err != nil {
 		return nil, err
 	}
-	if len(receipts) <= int(index) {
+	if uint64(len(receipts)) <= index {
 		return nil, nil
 	}
 	receipt := receipts[index]
```
