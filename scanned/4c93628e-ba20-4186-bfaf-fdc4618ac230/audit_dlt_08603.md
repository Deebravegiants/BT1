# [?] fix: prevent panic in `FullNodeProxy` with empty node list (#12948)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2025-03-13
Source: https://github.com/filecoin-project/lotus/commit/b8718a8b00a782c0ab90b6243e820545678493b3
Type: security-commit

## Details
fix: prevent panic in `FullNodeProxy` with empty node list (#12948)

fix: prevent panic in FullNodeProxy with empty node list

fix: prevent panic in FullNodeProxy with empty node list

## Patch
### cli/util/api.go
```diff
@@ -239,6 +239,11 @@ func OnSingleNode(ctx context.Context) context.Context {
 }
 
 func FullNodeProxy[T api.FullNode](ins []T, outstr *api.FullNodeStruct) {
+	if len(ins) == 0 {
+		log.Errorf("FullNodeProxy called with empty node list")
+		return
+	}
+
 	outs := api.GetInternalStructs(outstr)
 
 	var rins []reflect.Value
```
