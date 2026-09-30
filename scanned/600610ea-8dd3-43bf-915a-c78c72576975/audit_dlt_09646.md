# [?] qa: fix race condition in p2p-policy test

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2021-11-08
Source: https://github.com/dogecoin/dogecoin/commit/0010eedd12e4dd8ef2eb1187fce9b2042664ae4b
Type: security-commit

## Details
qa: fix race condition in p2p-policy test

Fixes a race condition in p2p-policy tests by waiting for a reject
message rather than assuming it was received before a pong message

## Patch
### qa/rpc-tests/p2p-policy.py
```diff
@@ -37,6 +37,14 @@ def on_pong(self, conn, message):
     def on_reject(self, conn, message):
         self.rejects.append(message)
 
+    # wait for a rejection message
+    def wait_for_reject(self, num_rejects=None):
+        if num_rejects is None:
+            num_rejects = len(self.rejects)
+        def reject_received():
+            return len(self.rejects) > num_rejects
+        return wait_until(reject_received, timeout=10)
+
     # wait for verack to make sure the node accepts our connection attempt
     def wait_for_verack(self):
         def veracked():
@@ -175,8 +183,8 @@ def run_relay_test(self, output, expected_reject_code):
             assert_equal(self.recvNode.wait_for_tx_inv(tx.hash), True)
             assert_equal(len(self.sendNode.rejects), num_rejects)
         else:
-            # test that there was a rejection received with the correct code
-            assert_greater_than(len(self.sendNode.rejects), num_rejects)
+            # wait until there was a rejection received with the correct code
+            assert_equal(self.sendNode.wait_for_reject(num_rejects), True)
             assert_equal(self.sendNode.rejects[-1].code, expected_reject_code)
 
         return tx
```
