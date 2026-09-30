# [?] x/interchainstaking: keeper, types: fix non-determinism from map iteration (#141)

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2022-07-28
Source: https://github.com/quicksilver-zone/quicksilver/commit/2528354d24fd78e80855e2ad59b4c6bf6dce28d8
Type: security-commit

## Details
x/interchainstaking: keeper, types: fix non-determinism from map iteration (#141)

In removing stale delegations, the loop was non-deterministic due to
iterating over a map. This change fixes that by extracting the keys
firstly into a slice, sorting it then iterating using those.

Also while here fixed non-determinism in types.Error which produced
different results on each invocation of types.Error.Error() and added
a unit test to lock this behavior in and avoid regressions.

Fixes #140

## Patch
### x/interchainstaking/keeper/ibc_handlers.go
```diff
@@ -4,6 +4,7 @@ import (
 	"bytes"
 	"encoding/json"
 	"fmt"
+	"sort"
 	"strings"
 
 	//lint:ignore SA1019 ignore this!
@@ -544,7 +545,14 @@ func (k *Keeper) UpdateDelegationRecordsForAddress(ctx sdk.Context, zone *types.
 		}
 	}
 
-	for _, existingDelegation := range delMap {
+	sortedLeftAddrs := make([]string, 0, len(delMap))
+	for valAddr := range delMap {
+		sortedLeftAddrs = append(sortedLeftAddrs, valAddr)
+	}
+	sort.Strings(sortedLeftAddrs)
+
+	for _, existingValAddr := range sortedLeftAddrs {
+		existingDelegation := delMap[existingValAddr]
 		_, valAddr, _ := bech32.DecodeAndConvert(existingDelegation.ValidatorAddress)
 		data := stakingtypes.GetDelegationKey(delAddr, valAddr)
 
```

### x/interchainstaking/types/error.go
```diff
@@ -3,6 +3,7 @@ package types
 import (
 	"errors"
 	"fmt"
+	"sort"
 )
 
 var (
@@ -27,8 +28,14 @@ func (e Errors) Error() string {
 func (e Errors) details(d int) string {
 	str := "{"
 	d++
-	for k, v := range e.Errors {
-		str += indent(k, v, d)
+
+	keys := make([]string, 0, len(e.Errors))
+	for k := range e.Errors {
+		keys = append(keys, k)
+	}
+	sort.Strings(keys)
+	for _, key := range keys {
+		str += indent(key, e.Errors[key], d)
 	}
 	d--
 	str += fmt.Sprintf("\n%v}", indentString("  ", d))
```

### x/interchainstaking/types/error_test.go
```diff
@@ -0,0 +1,30 @@
+package types
+
+import (
+	"errors"
+	"testing"
+)
+
+func TestErrorsDeterminism(t *testing.T) {
+	e := Errors{
+		Errors: map[string]error{
+			"a":    errors.New("a"),
+			"Z":    errors.New("Z"),
+			"🚨":    errors.New("🚨"),
+			"a🚨":   errors.New("a🚨"),
+			"ABC":  errors.New("ABC"),
+			"1one": errors.New("1one"),
+			"A":    errors.New("A"),
+			"X":    errors.New("X"),
+		},
+	}
+
+	e0 := e.Error()
+
+	for i := 0; i < 100; i++ {
+		ei := e.Error()
+		if ei != e0 {
+			t.Errorf("Iteration #%d produced non-deterministic data\n\tGot:  %q\n\tWant: %q", i+1, ei, e0)
+		}
+	}
+}
```
