# [?] fix(p2p): fix race condition caused by startTestNetwork (#801)

## Summary
Severity: Unknown
Chain: Rollkit
Component: rollkit/rollkit
Published: 2023-03-23
Source: https://github.com/evstack/ev-node/commit/b62e97f384fc3ba5c14a84fa6edafca132a1765c
Type: security-commit

## Details
fix(p2p): fix race condition caused by startTestNetwork (#801)

The `require.NotEmpty` utility reads through the struct fields of the
Host via reflection, while the internal background routine in the host
also accesses its field, causing race conditions. The fix is to use
`require.NotNil` as it only checks whether the Host is nil or not
without accessing its internal fields

## Patch
### p2p/utils_test.go
```diff
@@ -80,7 +80,7 @@ func startTestNetwork(ctx context.Context, t *testing.T, n int, conf map[int]hos
 			require.NoError(err)
 			host, err := mnet.AddPeer(privKey, addr)
 			require.NoError(err)
-			require.NotEmpty(host)
+			require.NotNil(host)
 		} else {
 			_, err := mnet.GenPeer()
 			require.NoError(err)
```
