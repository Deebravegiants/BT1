# [?] fix: remove debug panic from previous commit

## Summary
Severity: Unknown
Chain: ZK
Component: Consensys-Incorporated/gnark
Published: 2023-12-11
Source: https://github.com/Consensys-Incorporated/gnark/commit/59e16719c606f0691d49d545751dcf2dc21cfebb
Type: security-commit

## Details
fix: remove debug panic from previous commit

## Patch
### test/unsafekzg/kzgsrs.go
```diff
@@ -103,7 +103,6 @@ func NewSRS(ccs constraint.ConstraintSystem, opts ...Option) (canonical kzg.SRS,
 			return
 		} else {
 			log.Debug().Str("key", key).Err(err).Msg("SRS not found in fs cache")
-			panic(err)
 		}
 	}
 
```
