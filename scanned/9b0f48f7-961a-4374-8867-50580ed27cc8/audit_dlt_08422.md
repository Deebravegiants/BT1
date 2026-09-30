# [?] evidence: fix data race in Pool.updateValToLastHeight() (#5100)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2020-07-08
Source: https://github.com/cometbft/cometbft/commit/58113e31aefd6275047549705d245605747a9287
Type: security-commit

## Details
evidence: fix data race in Pool.updateValToLastHeight() (#5100)

Fixes #5098.

Is this out in a public release? If so, I'll add a changelog entry as well, for backporting.

## Patch
### evidence/pool.go
```diff
@@ -712,6 +712,9 @@ func evMapKey(ev types.Evidence) string {
 }
 
 func (evpool *Pool) updateValToLastHeight(blockHeight int64, state sm.State) {
+	evpool.mtx.Lock()
+	defer evpool.mtx.Unlock()
+
 	// Update current validators & add new ones.
 	for _, val := range state.Validators.Validators {
 		evpool.valToLastHeight[string(val.Address)] = blockHeight
```
