# [?] Merge pull request #6574 from str4d/fix-mempool_packages-nondeterminism

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2023-04-18
Source: https://github.com/zcash/zcash/commit/65e90a7964bac2bd06e3d5b35e8cf71ec3ef42f9
Type: security-commit

## Details
Merge pull request #6574 from str4d/fix-mempool_packages-nondeterminism

Fix `mempool_packages` nondeterminism

## Patch
### qa/rpc-tests/mempool_packages.py
```diff
@@ -103,9 +103,17 @@ def run_test(self):
             print("too-long-ancestor-chain successfully rejected")
 
         # Check that prioritising a tx before it's added to the mempool works
-        self.nodes[0].generate(1)
+        [blockhash] = self.nodes[0].generate(1)
+        # Ensure that node 1 receives this block before we invalidate it. Otherwise there
+        # is a race between node 1 sending a getdata to node 0, and node 0 invalidating
+        # the block, that when triggered causes:
+        # - node 0 to ignore node 1's "old" getdata;
+        # - node 1 to timeout and disconnect node 0;
+        # - node 0 and node 1 to have different chain tips, so sync_blocks times out.
+        self.sync_all()
+        assert_equal(self.nodes[0].getrawmempool(True), {})
         self.nodes[0].prioritisetransaction(chain[-1], None, 2000)
-        self.nodes[0].invalidateblock(self.nodes[0].getbestblockhash())
+        self.nodes[0].invalidateblock(blockhash)
         mempool = self.nodes[0].getrawmempool(True)
 
         descendant_fees = 0
@@ -117,6 +125,11 @@ def run_test(self):
 
         # TODO: check that node1's mempool is as expected
 
+        # Reconsider the above block to clear the mempool again before the next test phase.
+        self.nodes[0].reconsiderblock(blockhash)
+        assert_equal(self.nodes[0].getbestblockhash(), blockhash)
+        assert_equal(self.nodes[0].getrawmempool(True), {})
+
         # TODO: test ancestor size limits
 
         # Now test descendant chain limits
```
