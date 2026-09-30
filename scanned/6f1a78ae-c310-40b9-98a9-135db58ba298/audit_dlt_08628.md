# [?] Merge pull request #9241 from filecoin-project/fix/control-list-panic

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-09-16
Source: https://github.com/filecoin-project/lotus/commit/e3d59288fe9761252875d1dfe474b1a3f3ce1c73
Type: security-commit

## Details
Merge pull request #9241 from filecoin-project/fix/control-list-panic

fix: cli: fix panic in `lotus-miner actor control list`

## Patch
### cmd/lotus-miner/actor.go
```diff
@@ -549,7 +549,9 @@ var actorControlList = &cli.Command{
 			}
 			kstr := k.String()
 			if !cctx.Bool("verbose") {
-				kstr = kstr[:9] + "..."
+				if len(kstr) > 9 {
+					kstr = kstr[:6] + "..."
+				}
 			}
 
 			bstr := types.FIL(b).String()
```

### cmd/lotus-shed/actor.go
```diff
@@ -378,7 +378,9 @@ var actorControlList = &cli.Command{
 
 			kstr := k.String()
 			if !cctx.Bool("verbose") {
-				kstr = kstr[:9] + "..."
+				if len(kstr) > 9 {
+					kstr = kstr[:6] + "..."
+				}
 			}
 
 			bstr := types.FIL(b).String()
```
