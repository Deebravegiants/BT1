# [?] core/state: fix a panic in tests caused by a nil balance in gen accnt

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-10-18
Source: https://github.com/etclabscore/core-geth/commit/819c967398cf887412f23414f3537cd889aca143
Type: security-commit

## Details
core/state: fix a panic in tests caused by a nil balance in gen accnt

Date: 2023-10-18 07:34:25-06:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### core/state/statedb.go
```diff
@@ -374,7 +374,7 @@ func (s *StateDB) HasSelfDestructed(addr common.Address) bool {
 // AddBalance adds amount to the account associated with addr.
 func (s *StateDB) AddBalance(addr common.Address, amount *big.Int) {
 	stateObject := s.GetOrNewStateObject(addr)
-	if stateObject != nil {
+	if stateObject != nil && amount != nil {
 		stateObject.AddBalance(amount)
 	}
 }
```
