# [?] Fix crash in validateaddress with -disablewallet

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2015-11-09
Source: https://github.com/dogecoin/dogecoin/commit/2980a18572dbe6173c41afc037b0cefe367d935c
Type: security-commit

## Details
Fix crash in validateaddress with -disablewallet

Fix a null pointer dereference in validateaddress with -disablewallet. Also add a regression testcase.

## Patch
### qa/pull-tester/rpc-tests.py
```diff
@@ -68,6 +68,7 @@
     'decodescript.py',
     'p2p-fullblocktest.py',
     'blockchain.py',
+    'disablewallet.py',
 ]
 testScriptsExt = [
     'bip65-cltv.py',
```

### qa/rpc-tests/disablewallet.py
```diff
@@ -0,0 +1,32 @@
+#!/usr/bin/env python2
+# Copyright (c) 2014 The Bitcoin Core developers
+# Distributed under the MIT software license, see the accompanying
+# file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#
+# Exercise API with -disablewallet.
+#
+
+from test_framework.test_framework import BitcoinTestFramework
+from test_framework.util import *
+
+class DisableWalletTest (BitcoinTestFramework):
+
+    def setup_chain(self):
+        print("Initializing test directory "+self.options.tmpdir)
+        initialize_chain_clean(self.options.tmpdir, 1)
+
+    def setup_network(self, split=False):
+        self.nodes = start_nodes(1, self.options.tmpdir, [['-disablewallet']])
+        self.is_network_split = False
+        self.sync_all()
+
+    def run_test (self):
+        # Check regression: https://github.com/bitcoin/bitcoin/issues/6963#issuecomment-154548880
+        x = self.nodes[0].validateaddress('3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy')
+        assert(x['isvalid'] == False)
+        x = self.nodes[0].validateaddress('mneYUmWYsuk7kySiURxCi3AGxrAqZxLgPZ')
+        assert(x['isvalid'] == True)
+
+if __name__ == '__main__':
+    DisableWalletTest ().main ()
```

### src/rpcmisc.cpp
```diff
@@ -117,7 +117,7 @@ class DescribeAddressVisitor : public boost::static_visitor<UniValue>
         UniValue obj(UniValue::VOBJ);
         CPubKey vchPubKey;
         obj.push_back(Pair("isscript", false));
-        if (pwalletMain->GetPubKey(keyID, vchPubKey)) {
+        if (pwalletMain && pwalletMain->GetPubKey(keyID, vchPubKey)) {
             obj.push_back(Pair("pubkey", HexStr(vchPubKey)));
             obj.push_back(Pair("iscompressed", vchPubKey.IsCompressed()));
         }
@@ -128,7 +128,7 @@ class DescribeAddressVisitor : public boost::static_visitor<UniValue>
         UniValue obj(UniValue::VOBJ);
         CScript subscript;
         obj.push_back(Pair("isscript", true));
-        if (pwalletMain->GetCScript(scriptID, subscript)) {
+        if (pwalletMain && pwalletMain->GetCScript(scriptID, subscript)) {
             std::vector<CTxDestination> addresses;
             txnouttype whichType;
             int nRequired;
```
