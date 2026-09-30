# [?] [qa] Another attempt to fix race condition in p2p-compactblocks.py

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-10-04
Source: https://github.com/dogecoin/dogecoin/commit/6976db2f4687d575e1b4bee5aaf1d93a794f23c3
Type: security-commit

## Details
[qa] Another attempt to fix race condition in p2p-compactblocks.py

sync_with_ping() only guarantees that the node has processed messages
it's received from the peer, not that block announcements from the node have
made it back to the peer.  Replace sync_with_ping() with an explicit check that
the node's tip has been announced.

## Patch
### qa/rpc-tests/p2p-compactblocks.py
```diff
@@ -28,6 +28,10 @@ def __init__(self):
         self.last_getblocktxn = None
         self.last_block = None
         self.last_blocktxn = None
+        # Store the hashes of blocks we've seen announced.
+        # This is for synchronizing the p2p message traffic,
+        # so we can eg wait until a particular block is announced.
+        self.set_announced_blockhashes = set()
 
     def on_sendcmpct(self, conn, message):
         self.last_sendcmpct = message
@@ -38,14 +42,22 @@ def on_block(self, conn, message):
     def on_cmpctblock(self, conn, message):
         self.last_cmpctblock = message
         self.block_announced = True
+        self.last_cmpctblock.header_and_shortids.header.calc_sha256()
+        self.set_announced_blockhashes.add(self.last_cmpctblock.header_and_shortids.header.sha256)
 
     def on_headers(self, conn, message):
         self.last_headers = message
         self.block_announced = True
+        for x in self.last_headers.headers:
+            x.calc_sha256()
+            self.set_announced_blockhashes.add(x.sha256)
 
     def on_inv(self, conn, message):
         self.last_inv = message
-        self.block_announced = True
+        for x in self.last_inv.inv:
+            if x.type == 2:
+                self.block_announced = True
+                self.set_announced_blockhashes.add(x.hash)
 
     def on_getdata(self, conn, message):
         self.last_getdata = message
@@ -85,6 +97,12 @@ def request_headers_and_sync(self, locator, hashstop=0):
         assert(self.received_block_announcement())
         self.clear_block_announcement()
 
+    # Block until a block announcement for a particular block hash is
+    # received.
+    def wait_for_block_announcement(self, block_hash, timeout=30):
+        def received_hash():
+            return (block_hash in self.set_announced_blockhashes)
+        return wait_until(received_hash, timeout=timeout)
 
 class CompactBlocksTest(BitcoinTestFramework):
     def __init__(self):
@@ -237,7 +255,9 @@ def test_compactblock_construction(self):
         for i in range(num_transactions):
             self.nodes[0].sendtoaddress(address, 0.1)
 
-        self.test_node.sync_with_ping()
+        # Wait until we've seen the block announcement for the resulting tip
+        tip = int(self.nodes[0].getbestblockhash(), 16)
+        assert(self.test_node.wait_for_block_announcement(tip))
 
         # Now mine a block, and look at the resulting compact block.
         self.test_node.clear_block_announcement()
```
