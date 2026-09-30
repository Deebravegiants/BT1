# [?] Fixes eth.hashrate panic #393 (#409)

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2018-06-13
Source: https://github.com/Consensys-inc-archive/quorum/commit/4bfaedf312d0f4cc8d170209b68dd9f724973284
Type: security-commit

## Details
Fixes eth.hashrate panic #393 (#409)

## Patch
### consensus/ethash/ethash.go
```diff
@@ -562,6 +562,9 @@ func (ethash *Ethash) SetThreads(threads int) {
 // Hashrate implements PoW, returning the measured rate of the search invocations
 // per second over the last minute.
 func (ethash *Ethash) Hashrate() float64 {
+	if(ethash.hashrate == nil){
+		return 0
+	}
 	return ethash.hashrate.Rate1()
 }
 
```
