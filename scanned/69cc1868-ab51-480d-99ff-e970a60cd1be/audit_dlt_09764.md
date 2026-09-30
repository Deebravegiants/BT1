# [?] fix overflow todo

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-02-20
Source: https://github.com/onflow/flow-go/commit/6a67aeb41b7c407232ca6cc404f56d850d0412ca
Type: security-commit

## Details
fix overflow todo

## Patch
### fvm/inspection/token_changes.go
```diff
@@ -572,31 +572,39 @@ func (t accountTokens) add(id string, value uint64) {
 
 // diffAccountTokens will potentially modify before and after, so they should not be reused
 // after this call.
-// potential overflows
-// TODO: consider changing AccountChange to a larger type than int64
 func diffAccountTokens(before accountTokens, after accountTokens) AccountChange {
 	change := make(AccountChange)
 
 	for k, a := range after {
 		if b, ok := before[k]; ok {
 			if a > b {
-				change[k] = int64(a - b)
+				change[k] = safeUint64ToInt64(a - b)
 			} else if b > a {
-				change[k] = -int64(b - a)
+				change[k] = -safeUint64ToInt64(b - a)
 			}
 			delete(before, k)
 		} else {
-			change[k] = int64(a)
+			change[k] = safeUint64ToInt64(a)
 		}
 	}
 
 	for k, v := range before {
-		change[k] = -int64(v)
+		change[k] = -safeUint64ToInt64(v)
 	}
 
 	return change
 }
 
+// safeUint64ToInt64 converts a uint64 to int64, capping at math.MaxInt64 if the value
+// would overflow. If a value is capped, it will cause a mismatch in the token accounting
+// which will be logged and raise attention anyway.
+func safeUint64ToInt64(v uint64) int64 {
+	if v > math.MaxInt64 {
+		return math.MaxInt64
+	}
+	return int64(v)
+}
+
 type forEachCallback func(owner string, key string, value []byte) error
 
 type registers interface {
```
