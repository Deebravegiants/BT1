# [?] ethclient: fix panic when requesting missing blocks (#26817)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-03-07
Source: https://github.com/ethereum/go-ethereum/commit/4688d3c8f45cab05329906d96d9c63ba9cd9f398
Type: security-commit

## Details
ethclient: fix panic when requesting missing blocks (#26817)

This fixes a regression introduced by #26723.
Fixes #26816.

## Patch
### ethclient/ethclient.go
```diff
@@ -113,15 +113,19 @@ func (ec *Client) getBlock(ctx context.Context, method string, args ...interface
 	err := ec.c.CallContext(ctx, &raw, method, args...)
 	if err != nil {
 		return nil, err
-	} else if len(raw) == 0 {
-		return nil, ethereum.NotFound
 	}
+
 	// Decode header and transactions.
 	var head *types.Header
-	var body rpcBlock
 	if err := json.Unmarshal(raw, &head); err != nil {
 		return nil, err
 	}
+	// When the block is not found, the API returns JSON null.
+	if head == nil {
+		return nil, ethereum.NotFound
+	}
+
+	var body rpcBlock
 	if err := json.Unmarshal(raw, &body); err != nil {
 		return nil, err
 	}
```
