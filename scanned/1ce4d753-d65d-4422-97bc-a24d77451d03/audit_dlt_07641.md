# [?] console: fix some crashes/errors in the bridge (#21050)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2020-05-11
Source: https://github.com/ethereum/go-ethereum/commit/bd60295de56b04a435fc2a0b31d3d18a34cd3843
Type: security-commit

## Details
console: fix some crashes/errors in the bridge (#21050)

Fixes #21046

## Patch
### console/bridge.go
```diff
@@ -229,6 +229,9 @@ func (b *bridge) readPinAndReopenWallet(call jsre.Call) (goja.Value, error) {
 // original RPC method (saved in jeth.unlockAccount) with it to actually execute
 // the RPC call.
 func (b *bridge) UnlockAccount(call jsre.Call) (goja.Value, error) {
+	if nArgs := len(call.Arguments); nArgs < 2 {
+		return nil, fmt.Errorf("usage: unlockAccount(account, [ password, duration ])")
+	}
 	// Make sure we have an account specified to unlock.
 	if call.Argument(0).ExportType().Kind() != reflect.String {
 		return nil, fmt.Errorf("first argument must be the account to unlock")
@@ -272,6 +275,9 @@ func (b *bridge) UnlockAccount(call jsre.Call) (goja.Value, error) {
 // prompt to acquire the passphrase and executes the original RPC method (saved in
 // jeth.sign) with it to actually execute the RPC call.
 func (b *bridge) Sign(call jsre.Call) (goja.Value, error) {
+	if nArgs := len(call.Arguments); nArgs < 2 {
+		return nil, fmt.Errorf("usage: sign(message, account, [ password ])")
+	}
 	var (
 		message = call.Argument(0)
 		account = call.Argument(1)
@@ -307,6 +313,9 @@ func (b *bridge) Sign(call jsre.Call) (goja.Value, error) {
 
 // Sleep will block the console for the specified number of seconds.
 func (b *bridge) Sleep(call jsre.Call) (goja.Value, error) {
+	if nArgs := len(call.Arguments); nArgs < 1 {
+		return nil, fmt.Errorf("usage: sleep(<number of seconds>)")
+	}
 	if !isNumber(call.Argument(0)) {
 		return nil, fmt.Errorf("usage: sleep(<number of seconds>)")
 	}
@@ -334,7 +343,7 @@ func (b *bridge) SleepBlocks(call jsre.Call) (goja.Value, error) {
 		blocks = call.Argument(0).ToInteger()
 	}
 	if nArgs >= 2 {
-		if isNumber(call.Argument(1)) {
+		if !isNumber(call.Argument(1)) {
 			return nil, fmt.Errorf("expected number as second argument")
 		}
 		sleep = call.Argument(1).ToInteger()
```
