# [?] changing CAmount (is a int64_t) to arith_uint256 for nTotalAmount in CCoinsStats to prevent overflow

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2015-08-04
Source: https://github.com/dogecoin/dogecoin/commit/cf46c981a4bec56c54db1583bd335b6a8d641589
Type: security-commit

## Details
changing CAmount (is a int64_t) to arith_uint256 for nTotalAmount in CCoinsStats to prevent overflow

## Patch
### src/coins.h
```diff
@@ -10,6 +10,7 @@
 #include "memusage.h"
 #include "serialize.h"
 #include "uint256.h"
+#include "arith_uint256.h"
 
 #include <assert.h>
 #include <stdint.h>
@@ -305,7 +306,7 @@ struct CCoinsStats
     uint64_t nTransactionOutputs;
     uint64_t nSerializedSize;
     uint256 hashSerialized;
-    CAmount nTotalAmount;
+    arith_uint256 nTotalAmount;
 
     CCoinsStats() : nHeight(0), nTransactions(0), nTransactionOutputs(0), nSerializedSize(0), nTotalAmount(0) {}
 };
```

### src/rpcserver.cpp
```diff
@@ -140,6 +140,13 @@ Value ValueFromAmount(const CAmount& amount)
     return (double)amount / (double)COIN;
 }
 
+Value ValueFromAmount(const arith_uint256& amount)
+{
+    return amount.getdouble() / (double)COIN;
+}
+
+
+
 uint256 ParseHashV(const Value& v, string strName)
 {
     string strHex;
```

### src/rpcserver.h
```diff
@@ -9,6 +9,7 @@
 #include "amount.h"
 #include "rpcprotocol.h"
 #include "uint256.h"
+#include "arith_uint256.h"
 
 #include <list>
 #include <map>
@@ -139,6 +140,7 @@ extern void ShutdownRPCMining();
 extern int64_t nWalletUnlockTime;
 extern CAmount AmountFromValue(const json_spirit::Value& value);
 extern json_spirit::Value ValueFromAmount(const CAmount& amount);
+extern json_spirit::Value ValueFromAmount(const arith_uint256& amount);
 extern double GetDifficulty(const CBlockIndex* blockindex = NULL);
 extern std::string HelpRequiringPassphrase();
 extern std::string HelpExampleCli(std::string methodname, std::string args);
```

### src/txdb.cpp
```diff
@@ -10,6 +10,7 @@
 #include "main.h"
 #include "pow.h"
 #include "uint256.h"
+#include "arith_uint256.h"
 
 #include <stdint.h>
 
@@ -110,7 +111,7 @@ bool CCoinsViewDB::GetStats(CCoinsStats &stats) const {
     CHashWriter ss(SER_GETHASH, PROTOCOL_VERSION);
     stats.hashBlock = GetBestBlock();
     ss << stats.hashBlock;
-    CAmount nTotalAmount = 0;
+    arith_uint256 nTotalAmount = 0;
     while (pcursor->Valid()) {
         boost::this_thread::interruption_point();
         try {
```
