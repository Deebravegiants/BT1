# [?] fix sim val number being non deterministic (#5991)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-08-08
Source: https://github.com/osmosis-labs/osmosis/commit/9f54edde21fc20c40baea3943cb065e6cad63d5b
Type: security-commit

## Details
fix sim val number being non deterministic (#5991)

## Patch
### tests/simulator/state.go
```diff
@@ -137,7 +137,7 @@ func AppStateRandomizedFn(
 	// number of bonded accounts
 	initialStake := r.Int63n(1e12)
 	// Don't allow 0 validators to start off with
-	numInitiallyBonded := int64(rand.Intn(299)) + 1
+	numInitiallyBonded := int64(r.Intn(299)) + 1
 
 	if numInitiallyBonded > numAccs {
 		numInitiallyBonded = numAccs
```
