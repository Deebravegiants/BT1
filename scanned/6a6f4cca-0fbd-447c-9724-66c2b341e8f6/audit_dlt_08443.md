# [?] Add panic guard, bug fix (#1005)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2022-02-28
Source: https://github.com/osmosis-labs/osmosis/commit/9a78e778f44874bfdfcf8d4a684009ae3c857128
Type: security-commit

## Details
Add panic guard, bug fix (#1005)

## Patch
### CHANGELOG.md
```diff
@@ -45,6 +45,14 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 * [#984](https://github.com/osmosis-labs/osmosis/pull/984) Add wasm support to Dockerfile
 
+## [v7.0.2 - Carbon](https://github.com/osmosis-labs/osmosis/releases/tag/v7.0.2)
+
+This release fixes an instance of undefined behaviour present in v7.0.0.
+Parts of the code use a function called [`ApplyFuncIfNoErr`]() whose purpose is to catch errors, and if found undo state updates during its execution.
+It is intended to also catch panics and undo the problematic code's execution.
+Right now a panic in this code block would halt the node, as it would not know how to proceed.
+(But no state change would be committed)
+
 ## [v7.0.0 - Carbon](https://github.com/osmosis-labs/osmosis/releases/tag/v7.0.0)
 
 The Osmosis Carbon Release! The changes are primarily
```

### osmoutils/cache_ctx.go
```diff
@@ -1,17 +1,27 @@
 package osmoutils
 
 import (
+	"errors"
+	"fmt"
+
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
 
-// This function lets you run the function f, but if theres an error
+// This function lets you run the function f, but if theres an error or panic
 // drop the state machine change and log the error.
 // If there is no error, proceeds as normal (but with some slowdown due to SDK store weirdness)
 // Try to avoid usage of iterators in f.
-func ApplyFuncIfNoError(ctx sdk.Context, f func(ctx sdk.Context) error) error {
+func ApplyFuncIfNoError(ctx sdk.Context, f func(ctx sdk.Context) error) (err error) {
+	// Add a panic safeguard
+	defer func() {
+		if recovErr := recover(); recovErr != nil {
+			fmt.Println(recovErr)
+			err = errors.New("panic occured during execution")
+		}
+	}()
 	// makes a new cache context, which all state changes get wrapped inside of.
 	cacheCtx, write := ctx.CacheContext()
-	err := f(cacheCtx)
+	err = f(cacheCtx)
 	if err != nil {
 		ctx.Logger().Error(err.Error())
 	} else {
```

### x/superfluid/keeper/hooks.go
```diff
@@ -83,7 +83,7 @@ func (h Hooks) BeforeDelegationRemoved(ctx sdk.Context, delAddr sdk.AccAddress,
 func (h Hooks) AfterDelegationModified(ctx sdk.Context, delAddr sdk.AccAddress, valAddr sdk.ValAddress) {
 }
 func (h Hooks) BeforeValidatorSlashed(ctx sdk.Context, valAddr sdk.ValAddress, infractionHeight int64, slashFactor sdk.Dec, effectiveSlashFactor sdk.Dec) {
-	if slashFactor == sdk.ZeroDec() {
+	if slashFactor.IsZero() {
 		return
 	}
 	h.k.SlashLockupsForValidatorSlash(ctx, valAddr, infractionHeight, slashFactor)
```
