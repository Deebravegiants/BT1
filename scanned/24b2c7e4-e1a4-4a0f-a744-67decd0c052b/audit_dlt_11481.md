# [?] Push master @jackzampolin: fix test panic when client is nil

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/relayer
Published: 2020-04-15
Source: https://github.com/cosmos/relayer/commit/d22f1090cefc516c3c28bfa217c052a56809a18a
Type: security-commit

## Details
Push master @jackzampolin: fix test panic when client is nil

## Patch
### test/test_queries.go
```diff
@@ -24,6 +24,7 @@ func testClient(t *testing.T, src, dst *Chain) {
 
 	client, err := src.QueryClientState()
 	require.NoError(t, err)
+	require.NotNil(t, client)
 	require.Equal(t, client.ClientState.GetID(), src.PathEnd.ClientID)
 	require.Equal(t, client.ClientState.ClientType().String(), "tendermint")
 }
```
