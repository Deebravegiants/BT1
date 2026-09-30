# [?] fix(x/auth/tx): avoid panic from intoAnyV2 when v1.PublicKey is optional (#23148)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2025-01-03
Source: https://github.com/cosmos/cosmos-sdk/commit/07d5168d29d22e47ab927b368f12d2f63343e1c2
Type: security-commit

## Details
fix(x/auth/tx): avoid panic from intoAnyV2 when v1.PublicKey is optional (#23148)

## Patch
### CHANGELOG.md
```diff
@@ -51,6 +51,7 @@ Every module contains its own CHANGELOG.md. Please refer to the module you are i
 ### Bug Fixes
 
 * (query) [23002](https://github.com/cosmos/cosmos-sdk/pull/23002) Fix collection filtered pagination.
+* (x/auth/tx) [#23148](https://github.com/cosmos/cosmos-sdk/pull/23148) Avoid panic from intoAnyV2 when v1.PublicKey is optional.
 
 ### API Breaking Changes
 
```

### x/auth/tx/builder.go
```diff
@@ -293,9 +293,11 @@ func intoV2SignerInfo(v1s []*tx.SignerInfo) []*txv1beta1.SignerInfo {
 		modeInfoV2 := new(txv1beta1.ModeInfo)
 		intoV2ModeInfo(v1.ModeInfo, modeInfoV2)
 		v2 := &txv1beta1.SignerInfo{
-			PublicKey: intoAnyV2([]*codectypes.Any{v1.PublicKey})[0],
-			ModeInfo:  modeInfoV2,
-			Sequence:  v1.Sequence,
+			ModeInfo: modeInfoV2,
+			Sequence: v1.Sequence,
+		}
+		if v1.PublicKey != nil {
+			v2.PublicKey = intoAnyV2([]*codectypes.Any{v1.PublicKey})[0]
 		}
 		v2s[i] = v2
 	}
```

### x/auth/tx/builder_test.go
```diff
@@ -0,0 +1,15 @@
+package tx
+
+import (
+	"testing"
+
+	any "github.com/cosmos/gogoproto/types/any"
+	"github.com/stretchr/testify/require"
+
+	"github.com/cosmos/cosmos-sdk/types/tx"
+)
+
+func TestIntoV2SignerInfo(t *testing.T) {
+	require.NotNil(t, intoV2SignerInfo([]*tx.SignerInfo{{}}))
+	require.NotNil(t, intoV2SignerInfo([]*tx.SignerInfo{{PublicKey: &any.Any{}}}))
+}
```
