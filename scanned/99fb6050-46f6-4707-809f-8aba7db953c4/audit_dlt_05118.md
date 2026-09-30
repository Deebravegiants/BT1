# [?] [backport] test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2020-04-03
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/4d76dd59fd6562371a0daaeffe922a21304e5e87
Type: security-commit

## Details
[backport] test: add BIP37 remote crash bug [CVE-2013-5700] test to p2p_filter.py

Summary
---

This is a backport of https://github.com/bitcoin/bitcoin/pull/18515/commits/0ed2d8e07d3806d78d03a77d2153f22f9d733a07

Test plan
---

* `ninja all`
* `./test/functional/test_runner.py p2p_filter.py`

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
@@ -102,6 +103,10 @@ def run_test(self):
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
@@ -1441,6 +1441,25 @@ def __repr__(self):
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
@@ -67,6 +68,7 @@
     b"blocktxn": msg_blocktxn,
     b"cmpctblock": msg_cmpctblock,
     b"feefilter": msg_feefilter,
+    b"filteradd": msg_filteradd,
     b"filterclear": msg_filterclear,
     b"filterload": msg_filterload,
     b"getaddr": msg_getaddr,
@@ -372,6 +374,8 @@ def on_cmpctblock(self, message): pass
 
     def on_feefilter(self, message): pass
 
+    def on_filteradd(self, message): pass
+
     def on_filterclear(self, message): pass
 
     def on_filterload(self, message): pass
```
