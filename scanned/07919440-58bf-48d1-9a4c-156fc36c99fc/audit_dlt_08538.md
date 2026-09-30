# [?] logger: fix data race in tests (#5999)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2024-05-14
Source: https://github.com/algorand/go-algorand/commit/299b309a33c041493e43e3191a29d48db131500f
Type: security-commit

## Details
logger: fix data race in tests (#5999)

## Patch
### logging/log.go
```diff
@@ -308,7 +308,7 @@ func (l logger) SetOutput(w io.Writer) {
 }
 
 func (l logger) setOutput(w io.Writer) {
-	l.entry.Logger.Out = w
+	l.entry.Logger.SetOutput(w)
 }
 
 func (l logger) getOutput() io.Writer {
```
