# [?] Fix a nil dereference (copy-and-paste glitch)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-12-03
Source: https://github.com/harmony-one/harmony/commit/6ba20a4ba4893aff4b643ed27c789e341ca643ef
Type: security-commit

## Details
Fix a nil dereference (copy-and-paste glitch)

## Patch
### core/rawdb/accessors_chain.go
```diff
@@ -428,7 +428,7 @@ func ReadShardState(
 	if err2 != nil {
 		return nil, ctxerror.New("cannot decode sharding state",
 			"epoch", epoch,
-		).WithCause(err)
+		).WithCause(err2)
 	}
 	return ss, nil
 }
```
