# [?] Fix data race on cosmos provider config key (#677)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/relayer
Published: 2022-04-06
Source: https://github.com/cosmos/relayer/commit/e96b458e06339f635bfa58c14f4c329fd9e55307
Type: security-commit

## Details
Fix data race on cosmos provider config key (#677)

I have been seeing intermittent data races when running the integration
tests with the race detector enabled. This seems to fix those races. I
don't think it would be valid to change the config's key name at runtime
anyway.

## Patch
### relayer/provider/cosmos/query.go
```diff
@@ -64,10 +64,7 @@ func (cc *CosmosProvider) QueryTxs(ctx context.Context, page, limit int, events
 
 // QueryBalance returns the amount of coins in the relayer account
 func (cc *CosmosProvider) QueryBalance(ctx context.Context, keyName string) (sdk.Coins, error) {
-	if keyName != "" {
-		cc.PCfg.Key = keyName
-	}
-	addr, err := cc.Address()
+	addr, err := cc.ShowAddress(keyName)
 	if err != nil {
 		return nil, err
 	}
```
