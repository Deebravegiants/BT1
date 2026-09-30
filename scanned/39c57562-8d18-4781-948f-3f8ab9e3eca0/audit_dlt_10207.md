# [?] go/crasher: fix Caller information in global crasher

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2020-11-05
Source: https://github.com/oasisprotocol/oasis-core/commit/f5ef620b7a2ea392ae36d8f0e347969e3c858f4f
Type: security-commit

## Details
go/crasher: fix Caller information in global crasher

## Patch
### go/common/crash/crash.go
```diff
@@ -67,7 +67,10 @@ var crashGlobal *Crasher
 
 func init() {
 	crashGlobal = New(CrasherOptions{
-		CallerSkip: 1,
+		// Skip 2 stack frames to get the correct caller information.
+		// 2 since the global crasher is never invoked directly, but via the
+		// Here() function.
+		CallerSkip: 2,
 		CLIPrefix:  defaultCLIPrefix,
 	})
 }
```
