# [?] [qa] Fix race condition in p2p-compactblocks test

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-10-01
Source: https://github.com/dogecoin/dogecoin/commit/b5fd666984fdb7125cb809c773b36034f32128cc
Type: security-commit

## Details
[qa] Fix race condition in p2p-compactblocks test

Also fix a bug in the sync_with_ping() helper function

## Patch
### qa/rpc-tests/p2p-compactblocks.py
```diff
@@ -237,6 +237,8 @@ def test_compactblock_construction(self):
         for i in range(num_transactions):
             self.nodes[0].sendtoaddress(address, 0.1)
 
+        self.test_node.sync_with_ping()
+
         # Now mine a block, and look at the resulting compact block.
         self.test_node.clear_block_announcement()
         block_hash = int(self.nodes[0].generate(1)[0], 16)
```

### qa/rpc-tests/test_framework/mininode.py
```diff
@@ -1536,7 +1536,7 @@ def sync_with_ping(self, timeout=30):
         def received_pong():
             return (self.last_pong.nonce == self.ping_counter)
         self.send_message(msg_ping(nonce=self.ping_counter))
-        success = wait_until(received_pong, timeout)
+        success = wait_until(received_pong, timeout=timeout)
         self.ping_counter += 1
         return success
 
```
