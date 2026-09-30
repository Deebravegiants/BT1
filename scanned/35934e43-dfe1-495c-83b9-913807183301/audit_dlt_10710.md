# [?] attempt to fix non-deterministic failure of light/tx_relay_test (#1874)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-10-01
Source: https://github.com/Conflux-Chain/conflux-rust/commit/f047b6a5b6b34a5cd4c00e8ed1956e6ade8d41a5
Type: security-commit

## Details
attempt to fix non-deterministic failure of light/tx_relay_test (#1874)

## Patch
### tests/light/tx_relay_test.py
```diff
@@ -2,7 +2,7 @@
 
 # allow imports from parent directory
 # source: https://stackoverflow.com/a/11158224
-import os, sys
+import os, sys, time
 sys.path.insert(1, os.path.join(sys.path[0], '..'))
 
 from conflux.rpc import RpcClient
@@ -56,7 +56,7 @@ def generate_incorrect_block(self, node=None):
         blame_info['blame'] = "0x1"
         blame_info['deferredStateRoot'] = "0x1111111111111111111111111111111111111111111111111111111111111111"
 
-        return self.nodes[node].test_generateblockwithblameinfo(1, 0, blame_info)[0]
+        return self.nodes[node].test_generateblockwithblameinfo(1, 0, blame_info)
 
     def run_test(self):
         num_blocks = 100
@@ -129,17 +129,20 @@ def run_test(self):
 
         # generate some incorrect blocks
         # NOTE: we avoid 51% attacks as it could cause some inconsistency during syncing
-        for _ in range(num_blocks):
+        incorrect_blocks = []
+
+        for ii in range(num_blocks):
             if random.random() < 0.80:
                 self.generate_correct_block(FULLNODE0)
             else:
-                self.generate_incorrect_block(FULLNODE0)
+                hash = self.generate_incorrect_block(FULLNODE0)
+                incorrect_blocks.append((epoch_before_blamed_blocks + ii + 1, hash))
 
-        # generate some correct blocks to make sure we are confident about the previous one
-        sync_blocks(self.nodes[FULLNODE0:FULLNODE1])
+        self.log.info(f"Generated incorrect blocks: {incorrect_blocks}")
 
+        # generate some correct blocks to make sure we are confident about the previous one
         for _ in range(num_blocks):
-            self.generate_correct_block()
+            self.generate_correct_block(FULLNODE0)
 
         self.log.info(f"Pass 3 - blame info correct\n")
         # ------------------------------------------------
@@ -151,10 +154,12 @@ def run_test(self):
 
         latest_epoch = self.rpc[FULLNODE0].epoch_number()
 
+        # wait to make sure blame verification completes before we send queries
+        time.sleep(2)
+
         # check balances for each address on all nodes
         for (_, receiver, value) in txs:
             # pick random epoch from the ones that have all balance information
-            # this way, ~50% of our queries will have to deal with blaming blocks
             epoch = random.randint(epoch_before_blamed_blocks, latest_epoch - 26)
 
             node0_balance = self.rpc[FULLNODE0].get_balance(receiver)
```
