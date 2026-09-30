# [?] Fix race condition on test node shutdown

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2015-08-03
Source: https://github.com/dogecoin/dogecoin/commit/45a6cce971a96ebec6cc5d72921adbdde5ae4f18
Type: security-commit

## Details
Fix race condition on test node shutdown

## Patch
### qa/rpc-tests/test_framework/comptool.py
```diff
@@ -27,6 +27,20 @@
 
 global mininode_lock
 
+def wait_until(predicate, attempts=float('inf'), timeout=float('inf')):
+    attempt = 0
+    elapsed = 0
+
+    while attempt < attempts and elapsed < timeout:
+        with mininode_lock:
+            if predicate():
+                return True
+        attempt += 1
+        elapsed += 0.05
+        time.sleep(0.05)
+
+    return False
+
 class TestNode(NodeConnCB):
 
     def __init__(self, block_store, tx_store):
@@ -43,6 +57,10 @@ def __init__(self, block_store, tx_store):
         # a response
         self.pingMap = {} 
         self.lastInv = []
+        self.closed = False
+
+    def on_close(self, conn):
+        self.closed = True
 
     def add_connection(self, conn):
         self.conn = conn
@@ -132,61 +150,48 @@ class TestManager(object):
     def __init__(self, testgen, datadir):
         self.test_generator = testgen
         self.connections    = []
+        self.test_nodes     = []
         self.block_store    = BlockStore(datadir)
         self.tx_store       = TxStore(datadir)
         self.ping_counter   = 1
 
     def add_all_connections(self, nodes):
         for i in range(len(nodes)):
             # Create a p2p connection to each node
-            self.connections.append(NodeConn('127.0.0.1', p2p_port(i), 
-                        nodes[i], TestNode(self.block_store, self.tx_store)))
+            test_node = TestNode(self.block_store, self.tx_store)
+            self.test_nodes.append(test_node)
+            self.connections.append(NodeConn('127.0.0.1', p2p_port(i), nodes[i], test_node))
             # Make sure the TestNode (callback class) has a reference to its
             # associated NodeConn
-            self.connections[-1].cb.add_connection(self.connections[-1])
+            test_node.add_connection(self.connections[-1])
+
+    def wait_for_disconnections(self):
+        def disconnected():
+            return all(node.closed for node in self.test_nodes)
+        return wait_until(disconnected, timeout=10)
 
     def wait_for_verack(self):
-        sleep_time = 0.05
-        max_tries = 10 / sleep_time  # Wait at most 10 seconds
-        while max_tries > 0:
-            done = True
-            with mininode_lock:
-                for c in self.connections:
-                    if c.cb.verack_received is False:
-                        done = False
-                        break
-            if done:
-                break
-            time.sleep(sleep_time)
+        def veracked():
+            return all(node.verack_received for node in self.test_nodes)
+        return wait_until(veracked, timeout=10)
 
     def wait_for_pings(self, counter):
-        received_pongs = False
-        while received_pongs is not True:
-            time.sleep(0.05)
-            received_pongs = True
-            with mininode_lock:
-                for c in self.connections:
-                    if c.cb.received_ping_response(counter) is not True:
-                        received_pongs = False
-                        break
+        def received_pongs():
+            return all(node.received_ping_response(counter) for node in self.test_nodes)
+        return wait_until(received_pongs)
 
     # sync_blocks: Wait for all connections to request the blockhash given
     # then send get_headers to find out the tip of each node, and synchronize
     # the response by using a ping (and waiting for pong with same nonce).
     def sync_blocks(self, blockhash, num_blocks):
-        # Wait for nodes to request block (50ms sleep * 20 tries * num_blocks)
-        max_tries = 20*num_blocks
-        while max_tries > 0:
-            with mininode_lock:
-                results = [ blockhash in c.cb.block_request_map and
-                            c.cb.block_request_map[blockhash] for c in self.connections ]
-            if False not in results:
-                break
-            time.sleep(0.05)
-            max_tries -= 1
+        def blocks_requested():
+            return all(
+                blockhash in node.block_request_map and node.block_request_map[blockhash]
+                for node in self.test_nodes
+            )
 
         # --> error if not requested
-        if max_tries == 0:
+        if not wait_until(blocks_requested, attempts=20*num_blocks):
             # print [ c.cb.block_request_map for c in self.connections ]
             raise AssertionError("Not all nodes requested block")
         # --> Answer request (we did this inline!)
@@ -202,18 +207,14 @@ def sync_blocks(self, blockhash, num_blocks):
     # Analogous to sync_block (see above)
     def sync_transaction(self, txhash, num_events):
         # Wait for nodes to request transaction (50ms sleep * 20 tries * num_events)
-        max_tries = 20*num_events
-        while max_tries > 0:
-            with mininode_lock:
-                results = [ txhash in c.cb.tx_request_map and
-                            c.cb.tx_request_map[txhash] for c in self.connections ]
-            if False not in results:
-                break
-            time.sleep(0.05)
-            max_tries -= 1
+        def transaction_requested():
+            return all(
+                txhash in node.tx_request_map and node.tx_request_map[txhash]
+                for node in self.test_nodes
+            )
 
         # --> error if not requested
-        if max_tries == 0:
+        if not wait_until(transaction_requested, attempts=20*num_events):
             # print [ c.cb.tx_request_map for c in self.connections ]
             raise AssertionError("Not all nodes requested transaction")
         # --> Answer request (we did this inline!)
@@ -336,6 +337,7 @@ def run(self):
             print "Test %d: PASS" % test_number, [ c.rpc.getblockcount() for c in self.connections ]
             test_number += 1
 
+        [ c.disconnect_node() for c in self.connections ]
+        self.wait_for_disconnections()
         self.block_store.close()
         self.tx_store.close()
-        [ c.disconnect_node() for c in self.connections ]
```
