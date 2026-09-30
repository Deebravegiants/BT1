# [?] Merge #7480: Changed getnetworkhps value to double to avoid overflow.

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-02-09
Source: https://github.com/dogecoin/dogecoin/commit/b49a62379900762a39c2f00dcad764076426d954
Type: security-commit

## Details
Merge #7480: Changed getnetworkhps value to double to avoid overflow.

993d089 Changed getnetworkhps value to double to avoid overflow. (instagibbs)

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
