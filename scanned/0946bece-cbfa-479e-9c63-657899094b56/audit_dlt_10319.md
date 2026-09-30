# [?] Fix gas not being used on panic in queries

## Summary
Severity: Unknown
Chain: Secret
Component: scrtlabs/SecretNetwork
Published: 2020-07-27
Source: https://github.com/scrtlabs/SecretNetwork/commit/52a5db58deecb2e80fe94d05836534b9a1c0a4dd
Type: security-commit

## Details
Fix gas not being used on panic in queries

Co-authored-by: Reuven Podmazo <reuven@enigma.co>

## Patch
### go-cosmwasm/lib.go
```diff
@@ -168,7 +168,7 @@ func (w *Wasmer) Query(
 ) ([]byte, uint64, error) {
 	data, gasUsed, err := api.Query(w.cache, code, queryMsg, &gasMeter, &store, &goapi, &querier, gasLimit)
 	if err != nil {
-		return nil, 0, err
+		return nil, gasUsed, err
 	}
 
 	var resp types.QueryResponse
```
