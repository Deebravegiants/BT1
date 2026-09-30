# [?] internal/jsre: handle null and undefined to prevent crash (#23701)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-10-10
Source: https://github.com/ethereum/go-ethereum/commit/a6a0609b058e1a574abdee821eeeb02b324ee022
Type: security-commit

## Details
internal/jsre: handle null and undefined to prevent crash (#23701)

This prevents the console from crashing when auto-completing on
a variable or property that is null or undefined.

Fixes #23693

## Patch
### internal/jsre/completion.go
```diff
@@ -44,7 +44,7 @@ func getCompletions(vm *goja.Runtime, line string) (results []string) {
 	obj := vm.GlobalObject()
 	for i := 0; i < len(parts)-1; i++ {
 		v := obj.Get(parts[i])
-		if v == nil {
+		if v == nil || goja.IsNull(v) || goja.IsUndefined(v) {
 			return nil // No object was found
 		}
 		obj = v.ToObject(vm)
```
