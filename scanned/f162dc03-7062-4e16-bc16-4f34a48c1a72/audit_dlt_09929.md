# [?] Merge pull request #1915 from hyunsooda/klay-client-api-oob-fix

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2023-08-08
Source: https://github.com/kaiachain/kaia/commit/a60698352c3fafd5176df6bb9d5952bde3908c0e
Type: security-commit

## Details
Merge pull request #1915 from hyunsooda/klay-client-api-oob-fix

[Client] Nil-dereference of client API call fixed

## Patch
### client/klay_client.go
```diff
@@ -193,6 +193,9 @@ func (ec *Client) TransactionByHash(ctx context.Context, hash common.Hash) (tx *
 // There is a fast-path for transactions retrieved by TransactionByHash and
 // TransactionInBlock. Getting their sender address can be done without an RPC interaction.
 func (ec *Client) TransactionSender(ctx context.Context, tx *types.Transaction, block common.Hash, index uint) (common.Address, error) {
+	if tx == nil {
+		return common.Address{}, errors.New("Transaction must not be nil")
+	}
 	// Try to load the address from the cache.
 	sender, err := types.Sender(&senderFromServer{blockhash: block}, tx)
 	if err == nil {
```
