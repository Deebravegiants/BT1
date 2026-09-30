# [?] fix(utils): panic log formatting (#1814)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2022-10-26
Source: https://github.com/axelarnetwork/axelar-core/commit/dbdcfbc41b30e910a8a2607fba013f595b3f73bc
Type: security-commit

## Details
fix(utils): panic log formatting (#1814)

* fix(utils): panic log formatting

* Update utils/abci.go

Co-authored-by: Sammy Liu <sammy.liu@axelar.network>

Co-authored-by: Sammy Liu <sammy.liu@axelar.network>

## Patch
### utils/abci.go
```diff
@@ -22,7 +22,7 @@ func RunCached[T any](c sdk.Context, l Logger, f func(sdk.Context) (T, error)) T
 	defer func() {
 		if r := recover(); r != nil {
 			l.Logger(ctx).Error(fmt.Sprintf("recovered from panic in cached context: %v", r))
-			l.Logger(ctx).Error("%s", errors.Wrap(r, 1).Stack())
+			l.Logger(ctx).Error(string(errors.Wrap(r, 1).Stack()))
 		}
 	}()
 
```
