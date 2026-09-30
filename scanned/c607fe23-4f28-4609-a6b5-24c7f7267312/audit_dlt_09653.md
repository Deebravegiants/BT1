# [?] [qa] Fix race condition in sendheaders.py

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-10-06
Source: https://github.com/dogecoin/dogecoin/commit/b55d9411e7e1aa36ddabba3b942f2e1c736c1bd9
Type: security-commit

## Details
[qa] Fix race condition in sendheaders.py

Also de-duplicates code that has been moved to mininode

## Patch
### qa/rpc-tests/sendheaders.py
```diff
@@ -80,30 +80,26 @@
    Expect: disconnect.
 '''
 
-class BaseNode(NodeConnCB):
+direct_fetch_response_time = 0.05
+
+class BaseNode(SingleNodeConnCB):
     def __init__(self):
-        NodeConnCB.__init__(self)
-        self.connection = None
+        SingleNodeConnCB.__init__(self)
         self.last_inv = None
         self.last_headers = None
         self.last_block = None
-        self.ping_counter = 1
-        self.last_pong = msg_pong(0)
         self.last_getdata = None
-        self.sleep_time = 0.05
         self.block_announced = False
         self.last_getheaders = None
         self.disconnected = False
+        self.last_blockhash_announced = None
 
     def clear_last_announcement(self):
         with mininode_lock:
             self.block_announced = False
             self.last_inv = None
             self.last_headers = None
 
-    def add_connection(self, conn):
-        self.connection = conn
-
     # Request data for a list of block hashes
     def get_data(self, block_hashes):
         msg = msg_getdata()
@@ -122,17 +118,17 @@ def send_block_inv(self, blockhash):
         msg.inv = [CInv(2, blockhash)]
         self.connection.send_message(msg)
 
-    # Wrapper for the NodeConn's send_message function
-    def send_message(self, message):
-        self.connection.send_message(message)
-
     def on_inv(self, conn, message):
         self.last_inv = message
         self.block_announced = True
+        self.last_blockhash_announced = message.inv[-1].hash
 
     def on_headers(self, conn, message):
         self.last_headers = message
-        self.block_announced = True
+        if len(message.headers):
+            self.block_announced = True
+            message.headers[-1].calc_sha256()
+            self.last_blockhash_announced = message.headers[-1].sha256
 
     def on_block(self, conn, message):
         self.last_block = message.block
@@ -141,9 +137,6 @@ def on_block(self, conn, message):
     def on_getdata(self, conn, message):
         self.last_getdata = message
 
-    def on_pong(self, conn, message):
-        self.last_pong = message
-
     def on_getheaders(self, conn, message):
         self.last_getheaders = message
 
@@ -157,7 +150,7 @@ def check_last_announcement(self, headers=None, inv=None):
         expect_headers = headers if headers != None else []
         expect_inv = inv if inv != None else []
         test_function = lambda: self.block_announced
-        self.sync(test_function)
+        assert(wait_until(test_function, timeout=60))
         with mininode_lock:
             self.block_announced = False
 
@@ -180,43 +173,32 @@ def check_last_announcement(self, headers=None, inv=None):
         return success
 
     # Syncing helpers
-    def sync(self, test_function, timeout=60):
-        while timeout > 0:
-            with mininode_lock:
-                if test_function():
-                    return
-            time.sleep(self.sleep_time)
-            timeout -= self.sleep_time
-        raise AssertionError("Sync failed to complete")
-        
-    def sync_with_ping(self, timeout=60):
-        self.send_message(msg_ping(nonce=self.ping_counter))
-        test_function = lambda: self.last_pong.nonce == self.ping_counter
-        self.sync(test_function, timeout)
-        self.ping_counter += 1
-        return
-
     def wait_for_block(self, blockhash, timeout=60):
         test_function = lambda: self.last_block != None and self.last_block.sha256 == blockhash
-        self.sync(test_function, timeout)
+        assert(wait_until(test_function, timeout=timeout))
         return
 
     def wait_for_getheaders(self, timeout=60):
         test_function = lambda: self.last_getheaders != None
-        self.sync(test_function, timeout)
+        assert(wait_until(test_function, timeout=timeout))
         return
 
     def wait_for_getdata(self, hash_list, timeout=60):
         if hash_list == []:
             return
 
         test_function = lambda: self.last_getdata != None and [x.hash for x in self.last_getdata.inv] == hash_list
-        self.sync(test_function, timeout)
+        assert(wait_until(test_function, timeout=timeout))
         return
 
     def wait_for_disconnect(self, timeout=60):
         test_function = lambda: self.disconnected
-        self.sync(test_function, timeout)
+        assert(wait_until(test_function, timeout=timeout))
+        return
+
+    def wait_for_block_announcement(self, block_hash, timeout=60):
+        test_function = lambda: self.last_blockhash_announced == block_hash
+        assert(wait_until(test_function, timeout=timeout))
         return
 
     def send_header_for_blocks(self, new_blocks):
@@ -266,7 +248,9 @@ def mine_blocks(self, count):
     def mine_reorg(self, length):
         self.nodes[0].generate(length) # make sure all invalidated blocks are node0's
         sync_blocks(self.nodes, wait=0.1)
-        [x.clear_last_announcement() for x in self.p2p_connections]
+        for x in self.p2p_connections:
+            x.wait_for_block_announcement(int(self.nodes[0].getbestblockhash(), 16))
+            x.clear_last_announcement()
 
         tip_height = self.nodes[1].getblockcount()
         hash_to_invalidate = self.nodes[1].getblockhash(tip_height-(length-1))
@@ -495,7 +479,7 @@ def run_test(self):
 
         test_node.send_header_for_blocks(blocks)
         test_node.sync_with_ping()
-        test_node.wait_for_getdata([x.sha256 for x in blocks], timeout=test_node.sleep_time)
+        test_node.wait_for_getdata([x.sha256 for x in blocks], timeout=direct_fetch_response_time)
 
         [ test_node.send_message(msg_block(x)) for x in blocks ]
 
@@ -526,13 +510,13 @@ def run_test(self):
         # both blocks (same work as tip)
         test_node.send_header_for_blocks(blocks[1:2])
         test_node.sync_with_ping()
-        test_node.wait_for_getdata([x.sha256 for x in blocks[0:2]], timeout=test_node.sleep_time)
+        test_node.wait_for_getdata([x.sha256 for x in blocks[0:2]], timeout=direct_fetch_response_time)
 
         # Announcing 16 more headers should trigger direct fetch for 14 more
         # blocks
         test_node.send_header_for_blocks(blocks[2:18])
         test_node.sync_with_ping()
-        test_node.wait_for_getdata([x.sha256 for x in blocks[2:16]], timeout=test_node.sleep_time)
+        test_node.wait_for_getdata([x.sha256 for x in blocks[2:16]], timeout=direct_fetch_response_time)
 
         # Announcing 1 more header should not trigger any response
         test_node.last_getdata = None
```
