# [?] go-ipfs-config: fix: panic on invalid priority/flag values

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2020-06-16
Source: https://github.com/ipfs/kubo/commit/44e005e57709ee7e1b95270476d8a32aa0d23076
Type: security-commit

## Details
go-ipfs-config: fix: panic on invalid priority/flag values

## Patch
### config/types.go
```diff
@@ -56,6 +56,8 @@ const (
 )
 
 // WithDefault resolves the value of the flag given the provided default value.
+//
+// Panics if Flag is an invalid value.
 func (f Flag) WithDefault(defaultValue bool) bool {
 	switch f {
 	case False:
@@ -126,17 +128,30 @@ const (
 
 // WithDefault resolves the priority with the given default.
 //
-// If `defaultPriority` is Default/0, this function will return 0.
+// If defaultPriority is Default/0, this function will return 0.
+//
+// Panics if the priority has an invalid value (e.g., not DefaultPriority,
+// Disabled, or > 0).
 func (p Priority) WithDefault(defaultPriority Priority) (priority int64, enabled bool) {
 	switch p {
 	case Disabled:
 		return 0, false
 	case DefaultPriority:
-		if defaultPriority < 0 {
+		switch defaultPriority {
+		case Disabled:
 			return 0, false
+		case DefaultPriority:
+			return 0, true
+		default:
+			if defaultPriority <= 0 {
+				panic(fmt.Sprintf("invalid priority %d < 0", int64(defaultPriority)))
+			}
+			return int64(defaultPriority), true
 		}
-		return int64(defaultPriority), true
 	default:
+		if p <= 0 {
+			panic(fmt.Sprintf("invalid priority %d < 0", int64(p)))
+		}
 		return int64(p), true
 	}
 }
```
