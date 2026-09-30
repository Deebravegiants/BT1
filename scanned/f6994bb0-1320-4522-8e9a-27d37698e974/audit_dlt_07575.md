# [?] eth: fix panic in randomDuration when min equals max (#33193)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-11-18
Source: https://github.com/ethereum/go-ethereum/commit/e0d81d1e993ad6dc3e618cd06e56b7be916efd8e
Type: security-commit

## Details
eth: fix panic in randomDuration when min equals max (#33193)

Fixes a potential panic in `randomDuration` when `min == max` by
handling the edge case explicitly.

## Patch
### eth/dropper.go
```diff
@@ -145,6 +145,9 @@ func randomDuration(min, max time.Duration) time.Duration {
 	if min > max {
 		panic("min duration must be less than or equal to max duration")
 	}
+	if min == max {
+		return min
+	}
 	return time.Duration(mrand.Int63n(int64(max-min)) + int64(min))
 }
 
```
