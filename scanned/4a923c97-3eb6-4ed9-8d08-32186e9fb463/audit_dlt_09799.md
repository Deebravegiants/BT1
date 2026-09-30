# [?] Fix for possible panic. (#4627)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2024-02-13
Source: https://github.com/harmony-one/harmony/commit/d5956cee90c7487ab909e43802f0d74737d3e301
Type: security-commit

## Details
Fix for possible panic. (#4627)

## Patch
### core/state_processor.go
```diff
@@ -310,7 +310,17 @@ func ApplyTransaction(bc ChainContext, author *common.Address, gp *GasPool, stat
 	// Apply the transaction to the current state (included in the env)
 	result, err := ApplyMessage(vmenv, msg, gp)
 	if err != nil {
-		return nil, nil, nil, 0, errors.Wrapf(err, "apply failed from='%s' to='%s' balance='%s'", msg.From().Hex(), msg.To().Hex(), statedb.GetBalance(msg.From()).String())
+		if err != nil {
+			to := ""
+			if m := msg.To(); m != nil {
+				to = m.Hex()
+			}
+			balance := ""
+			if a := statedb.GetBalance(msg.From()); a != nil {
+				balance = a.String()
+			}
+			return nil, nil, nil, 0, errors.Wrapf(err, "apply failed from='%s' to='%s' balance='%s'", msg.From().Hex(), to, balance)
+		}
 	}
 	// Update the state with pending changes
 	var root []byte
```
