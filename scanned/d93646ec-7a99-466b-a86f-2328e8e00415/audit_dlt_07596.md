# [?] eth/tracers/native: fix possible crash in prestate tracer (#26351)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-12-13
Source: https://github.com/ethereum/go-ethereum/commit/fa97788c757a07c0dd038db5ef1a05ee9158e2e6
Type: security-commit

## Details
eth/tracers/native: fix possible crash in prestate tracer (#26351)

## Patch
### eth/tracers/native/prestate.go
```diff
@@ -45,7 +45,7 @@ type account struct {
 }
 
 func (a *account) exists() bool {
-	return a.Balance.Sign() != 0 || a.Nonce > 0 || len(a.Code) > 0 || len(a.Storage) > 0
+	return a.Nonce > 0 || len(a.Code) > 0 || len(a.Storage) > 0 || (a.Balance != nil && a.Balance.Sign() != 0)
 }
 
 type accountMarshaling struct {
```
