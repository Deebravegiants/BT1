# [?] Fix crash when mining with empty keypool.

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2015-08-18
Source: https://github.com/dogecoin/dogecoin/commit/20165769989ed5aa744af2b73dfcf9d5a5cf7aa0
Type: security-commit

## Details
Fix crash when mining with empty keypool.

Since the introduction of the ScriptForMining callback, the mining
functions (setgenerate and generate) crash with an assertion failure
(due to a NULL pointer script returned) if the keypool is empty.  Fix
this by giving a proper error.

## Patch
### qa/rpc-tests/keypool.py
```diff
@@ -73,6 +73,21 @@ def run_test(nodes, tmpdir):
     except JSONRPCException,e:
         assert(e.error['code']==-12)
 
+    # refill keypool with three new addresses
+    nodes[0].walletpassphrase('test', 12000)
+    nodes[0].keypoolrefill(3)
+    nodes[0].walletlock()
+
+    # drain them by mining
+    nodes[0].generate(1)
+    nodes[0].generate(1)
+    nodes[0].generate(1)
+    nodes[0].generate(1)
+    try:
+        nodes[0].generate(1)
+        raise AssertionError('Keypool should be exhausted after three addesses')
+    except JSONRPCException,e:
+        assert(e.error['code']==-12)
 
 def main():
     import optparse
```

### src/miner.cpp
```diff
@@ -444,8 +444,10 @@ void static BitcoinMiner(const CChainParams& chainparams)
     GetMainSignals().ScriptForMining(coinbaseScript);
 
     try {
-        //throw an error if no script was provided
-        if (!coinbaseScript->reserveScript.size())
+        // Throw an error if no script was provided.  This can happen
+        // due to some internal error but also if the keypool is empty.
+        // In the latter case, already the pointer is NULL.
+        if (!coinbaseScript || coinbaseScript->reserveScript.empty())
             throw std::runtime_error("No coinbase script available (mining requires a wallet)");
 
         while (true) {
```

### src/rpcmining.cpp
```diff
@@ -138,8 +138,12 @@ UniValue generate(const UniValue& params, bool fHelp)
     boost::shared_ptr<CReserveScript> coinbaseScript;
     GetMainSignals().ScriptForMining(coinbaseScript);
 
+    // If the keypool is exhausted, no script is returned at all.  Catch this.
+    if (!coinbaseScript)
+        throw JSONRPCError(RPC_WALLET_KEYPOOL_RAN_OUT, "Error: Keypool ran out, please call keypoolrefill first");
+
     //throw an error if no script was provided
-    if (!coinbaseScript->reserveScript.size())
+    if (coinbaseScript->reserveScript.empty())
         throw JSONRPCError(RPC_INTERNAL_ERROR, "No coinbase script available (mining requires a wallet)");
 
     {   // Don't keep cs_main locked
```
