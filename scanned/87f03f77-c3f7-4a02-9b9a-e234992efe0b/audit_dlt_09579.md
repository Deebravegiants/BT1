# [?] attempt to fix non-deterministic light node test failure

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-01-19
Source: https://github.com/Conflux-Chain/conflux-rust/commit/09407d7d4ec4155da1762234e8e5a5720b8efe6c
Type: security-commit

## Details
attempt to fix non-deterministic light node test failure

## Patch
### tests/light/rpc_test.py
```diff
@@ -434,8 +434,15 @@ def test_block_methods(self):
             txs.append(tx)
 
         block_hash = self.rpc[FULLNODE0].generate_block_with_fake_txs(txs)
-        self.rpc[FULLNODE0].generate_blocks(BLAME_CHECK_OFFSET) # make sure txs are executed
+
+        # make sure txs are executed
+        parent_hash = block_hash
+
+        for _ in range(BLAME_CHECK_OFFSET + 10):
+            parent_hash = self.rpc[FULLNODE0].generate_block_with_parent(parent_hash=parent_hash)
+
         sync_blocks(self.nodes)
+        time.sleep(1)
 
         # --------------------------
 
```
