# [?] fix(pruner): fix race condition in TestFindPruneableHeaders (#4792)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2026-02-19
Source: https://github.com/celestiaorg/celestia-node/commit/e291f26776a8dc5d9dce72d5ed0ba3aa4d4d373a
Type: security-commit

## Details
fix(pruner): fix race condition in TestFindPruneableHeaders (#4792)

## Patch
### pruner/service_test.go
```diff
@@ -258,7 +258,8 @@ func TestFindPruneableHeaders(t *testing.T) {
 			)
 			require.NoError(t, err)
 
-			err = serv.Start(ctx)
+			serv.ctx = ctx
+			err = serv.loadCheckpoint(ctx)
 			require.NoError(t, err)
 
 			lastPruned, err := serv.lastPruned(ctx)
```
