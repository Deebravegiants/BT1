# [?] Changed getnetworkhps value to double to avoid overflow.

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-02-08
Source: https://github.com/dogecoin/dogecoin/commit/993d089e82fc045d7b0f23e1a5dc934cba0e3306
Type: security-commit

## Details
Changed getnetworkhps value to double to avoid overflow.

## Patch
### src/rpc/mining.cpp
```diff
@@ -68,7 +68,7 @@ UniValue GetNetworkHashPS(int lookup, int height) {
     arith_uint256 workDiff = pb->nChainWork - pb0->nChainWork;
     int64_t timeDiff = maxTime - minTime;
 
-    return (int64_t)(workDiff.getdouble() / timeDiff);
+    return workDiff.getdouble() / timeDiff;
 }
 
 UniValue getnetworkhashps(const UniValue& params, bool fHelp)
```
