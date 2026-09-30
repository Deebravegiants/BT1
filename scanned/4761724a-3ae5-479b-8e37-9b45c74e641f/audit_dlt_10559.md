# [?] Fixes eth.hashrate panic #393 (#409)

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2018-06-13
Source: https://github.com/Consensys-inc-archive/quorum/commit/f3d1315269df2e4ff749d987cc119eb82d5bacb0
Type: security-commit

## Details
Fixes eth.hashrate panic #393 (#409)

## Patch
### consensus/ethash/ethash.go
```diff
@@ -583,6 +583,9 @@ func (ethash *Ethash) SetThreads(threads int) {
 // Hashrate implements PoW, returning the measured rate of the search invocations
 // per second over the last minute.
 func (ethash *Ethash) Hashrate() float64 {
+	if(ethash.hashrate == nil){
+		return 0
+	}
 	return ethash.hashrate.Rate1()
 }
 
```
