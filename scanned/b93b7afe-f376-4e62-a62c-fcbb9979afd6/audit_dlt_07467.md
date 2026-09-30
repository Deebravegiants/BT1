# [?] Merge bitcoin/bitcoin#27199: test: fix race condition in encrypted wallet rescan tests

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2023-03-16
Source: https://github.com/dashpay/dash/commit/0bc9aea9c991341d3f92f6d029437f9edd158909
Type: security-commit

## Details
Merge bitcoin/bitcoin#27199: test: fix race condition in encrypted wallet rescan tests

dbeca792a9980085d00be0f9d78187ca3a4d7cdc test: fix race condition in encrypted wallet rescan tests (ishaanam)

Pull request description:

  This fixes https://github.com/bitcoin/bitcoin/pull/26347#discussion_r1123340738

ACKs for top commit:
  MarcoFalke:
    nice re-ACK dbeca792a9980085d00be0f9d78187ca3a4d7cdc  🚜
  achow101:
    ACK dbeca792a9980085d00be0f9d78187ca3a4d7cdc

Tree-SHA512: 7127254ac0274b5bc8ba0242736e77464acbf1f6e3f6af098b4e47742124c336cd67dffdb385e1e8dbd3a8ae74acd073c99e82fa35c44a615fd7d22b29a0daf7

Co-authored-by: Andrew Chow <github@achow101.com>

## Patch
### test/functional/wallet_importdescriptors.py
```diff
@@ -15,6 +15,10 @@
 - `test_address()` is called to call getaddressinfo for an address on node1
   and test the values returned."""
 
+import threading
+
+from test_framework.authproxy import JSONRPCException
+from test_framework.blocktools import COINBASE_MATURITY
 from test_framework.test_framework import BitcoinTestFramework
 from test_framework.descriptors import descsum_create
 from test_framework.util import (
@@ -631,11 +635,26 @@ def run_test(self):
         descriptor["timestamp"] = 0
         descriptor["next_index"] = 0
 
-        batch = []
-        batch.append(encrypted_wallet.walletpassphrase.get_request("passphrase", 3))
-        batch.append(encrypted_wallet.importdescriptors.get_request([descriptor]))
+        encrypted_wallet.walletpassphrase("passphrase", 99999)
+        t = threading.Thread(target=encrypted_wallet.importdescriptors, args=([descriptor],))
+
+        with self.nodes[0].assert_debug_log(expected_msgs=[f'Rescan started from block 000008ca1832a4baf228eb1553c03d3a2c8e02399550dd6ea8d65cec3ef23d2e... (slow variant inspecting all blocks)'], timeout=5):
+            t.start()
+
+        # Set the passphrase timeout to 1 to test that the wallet remains unlocked during the rescan
+        self.nodes[0].cli("-rpcwallet=encrypted_wallet").walletpassphrase("passphrase", 1)
+
+        try:
+            self.nodes[0].cli("-rpcwallet=encrypted_wallet").walletlock()
+        except JSONRPCException as e:
+            assert e.error['code'] == -4 and "Error: the wallet is currently being used to rescan the blockchain for related transactions. Please call `abortrescan` before locking the wallet." in e.error['message']
+
+        try:
+            self.nodes[0].cli("-rpcwallet=encrypted_wallet").walletpassphrasechange("passphrase", "newpassphrase")
+        except JSONRPCException as e:
+            assert e.error['code'] == -4 and "Error: the wallet is currently being used to rescan the blockchain for related transactions. Please call `abortrescan` before changing the passphrase." in e.error['message']
 
-        encrypted_wallet.batch(batch)
+        t.join()
 
         assert_equal(temp_wallet.getbalance(), encrypted_wallet.getbalance())
 
```

### test/functional/wallet_transactiontime_rescan.py
```diff
@@ -5,8 +5,10 @@
 """Test transaction time during old block rescanning
 """
 
+import threading
 import time
 
+from test_framework.authproxy import JSONRPCException
 from test_framework.blocktools import COINBASE_MATURITY
 from test_framework.test_framework import BitcoinTestFramework
 from test_framework.util import (
@@ -201,14 +203,28 @@ def run_test(self):
             minernode.createwallet("encrypted_wallet", blank=True, passphrase="passphrase", descriptors=False)
             encrypted_wallet = minernode.get_wallet_rpc("encrypted_wallet")
 
-            encrypted_wallet.walletpassphrase("passphrase", 1)
+            encrypted_wallet.walletpassphrase("passphrase", 99999)
             encrypted_wallet.sethdseed(seed=hd_seed)
 
-            batch = []
-            batch.append(encrypted_wallet.walletpassphrase.get_request("passphrase", 3))
-            batch.append(encrypted_wallet.rescanblockchain.get_request())
+            t = threading.Thread(target=encrypted_wallet.rescanblockchain)
 
-            encrypted_wallet.batch(batch)
+            with minernode.assert_debug_log(expected_msgs=[f'Rescan started from block 000008ca1832a4baf228eb1553c03d3a2c8e02399550dd6ea8d65cec3ef23d2e... (slow variant inspecting all blocks)'], timeout=5):
+                t.start()
+
+            # set the passphrase timeout to 1 to test that the wallet remains unlocked during the rescan
+            minernode.cli("-rpcwallet=encrypted_wallet").walletpassphrase("passphrase", 1)
+
+            try:
+                minernode.cli("-rpcwallet=encrypted_wallet").walletlock()
+            except JSONRPCException as e:
+                assert e.error['code'] == -4 and "Error: the wallet is currently being used to rescan the blockchain for related transactions. Please call `abortrescan` before locking the wallet." in e.error['message']
+
+            try:
+                minernode.cli("-rpcwallet=encrypted_wallet").walletpassphrasechange("passphrase", "newpassphrase")
+            except JSONRPCException as e:
+                assert e.error['code'] == -4 and "Error: the wallet is currently being used to rescan the blockchain for related transactions. Please call `abortrescan` before changing the passphrase." in e.error['message']
+
+            t.join()
 
             assert_equal(encrypted_wallet.getbalance(), temp_wallet.getbalance())
 
```
