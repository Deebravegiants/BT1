# [?] test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-04-03
Source: https://github.com/litecoin-project/litecoin/commit/0ed2d8e07d3806d78d03a77d2153f22f9d733a07
Type: security-commit

## Details
test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py

## Patch
### test/functional/p2p_filter.py
```diff
@@ -11,6 +11,7 @@
     MSG_FILTERED_BLOCK,
     msg_getdata,
     msg_filterload,
+    msg_filteradd,
     msg_filterclear,
 )
 from test_framework.mininode import (
@@ -103,6 +104,10 @@ def run_test(self):
             txid = self.nodes[0].sendtoaddress(self.nodes[0].getnewaddress(), 7)
             filter_node.wait_for_tx(txid)
 
+        self.log.info("Check that division-by-zero remote crash bug [CVE-2013-5700] is fixed")
+        filter_node.send_and_ping(msg_filterload(data=b'', nHashFuncs=1))
+        filter_node.send_and_ping(msg_filteradd(data=b'letstrytocrashthisnode'))
+
 
 if __name__ == '__main__':
     FilterTest().main()
```

### test/functional/test_framework/messages.py
```diff
@@ -1356,6 +1356,25 @@ def __repr__(self):
             self.data, self.nHashFuncs, self.nTweak, self.nFlags)
 
 
+class msg_filteradd:
+    __slots__ = ("data")
+    command = b"filteradd"
+
+    def __init__(self, data):
+        self.data = data
+
+    def deserialize(self, f):
+        self.data = deser_string(f)
+
+    def serialize(self):
+        r = b""
+        r += ser_string(self.data)
+        return r
+
+    def __repr__(self):
+        return "msg_filteradd(data={})".format(self.data)
+
+
 class msg_filterclear:
     __slots__ = ()
     command = b"filterclear"
```

### test/functional/test_framework/mininode.py
```diff
@@ -30,6 +30,7 @@
     msg_blocktxn,
     msg_cmpctblock,
     msg_feefilter,
+    msg_filteradd,
     msg_filterclear,
     msg_filterload,
     msg_getaddr,
@@ -65,6 +66,7 @@
     b"blocktxn": msg_blocktxn,
     b"cmpctblock": msg_cmpctblock,
     b"feefilter": msg_feefilter,
+    b"filteradd": msg_filteradd,
     b"filterclear": msg_filterclear,
     b"filterload": msg_filterload,
     b"getaddr": msg_getaddr,
@@ -324,6 +326,7 @@ def on_block(self, message): pass
     def on_blocktxn(self, message): pass
     def on_cmpctblock(self, message): pass
     def on_feefilter(self, message): pass
+    def on_filteradd(self, message): pass
     def on_filterclear(self, message): pass
     def on_filterload(self, message): pass
     def on_getaddr(self, message): pass
```
