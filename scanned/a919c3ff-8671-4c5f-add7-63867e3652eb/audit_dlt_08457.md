# [?] bugfix(libs/header/p2p): fix data race in test (#1928)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-03-17
Source: https://github.com/celestiaorg/celestia-node/commit/5e5173cabd623097eae6463b8ff33da43acbe30b
Type: security-commit

## Details
bugfix(libs/header/p2p): fix data race in test (#1928)

## Patch
### libs/header/p2p/exchange_test.go
```diff
@@ -318,7 +318,6 @@ func TestExchange_HandleHeaderWithDifferentChainID(t *testing.T) {
 	hosts := createMocknet(t, 2)
 	exchg, store := createP2PExAndServer(t, hosts[0], hosts[1])
 	exchg.Params.chainID = "test"
-	require.NoError(t, exchg.Start(context.TODO()))
 
 	_, err := exchg.Head(context.Background())
 	require.Error(t, err)
```
