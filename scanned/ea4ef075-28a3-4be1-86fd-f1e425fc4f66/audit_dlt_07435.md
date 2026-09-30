# [?] Merge #15069: test: Fix rpc_net.py "pong" race condition

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2019-01-02
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/30e7ad4ca0fa63908ba9c8b7ed5c04b84258ec2e
Type: security-commit

## Details
Merge #15069: test: Fix rpc_net.py "pong" race condition

Summary:
de23739b22 test: Fix rpc_net.py "pong" race condition (Ben Woosley)

Pull request description:

  Prior to this change, the test fails with KeyError if pong has
  a zero value at the time this is called, as getpeerinfo's
  bytesrecv_per_msg result excludes zero-values.

  Combined these to a single wait_until as well, which will be a bit more
  forgiving re the timeout while still enforcing the same 2 seconds
  overall.

  https://ci.appveyor.com/project/DrahtBot/bitcoin/builds/21310881#L62

Tree-SHA512: dc60f95a0e139c104fd81c8a7e0c9b3c25907de26c9d4e5976ae490e8ed5db0f0c492cd0e996ef6b5eb02cae82a62d4551ed36f95601871b19472050b3247bc0

Backport Core [[https://github.com/bitcoin/bitcoin/pull/15069 | PR15069]]

Test Plan:
```
test_runner.py rpc_net  # run a few times
```

Reviewers: #bitcoin_abc, Fabien

Reviewed By: #bitcoin_abc, Fabien

Differential Revision: https://reviews.bitcoinabc.org/D5829

## Patch
### test/functional/rpc_net.py
```diff
@@ -76,9 +76,13 @@ def _test_getnettotals(self):
         peer_info_after_ping = self.nodes[0].getpeerinfo()
         for before, after in zip(peer_info, peer_info_after_ping):
             assert_greater_than_or_equal(
-                after['bytesrecv_per_msg']['pong'], before['bytesrecv_per_msg']['pong'] + 32)
+                after['bytesrecv_per_msg'].get(
+                    'pong', 0), before['bytesrecv_per_msg'].get(
+                    'pong', 0) + 32)
             assert_greater_than_or_equal(
-                after['bytessent_per_msg']['ping'], before['bytessent_per_msg']['ping'] + 32)
+                after['bytessent_per_msg'].get(
+                    'ping', 0), before['bytessent_per_msg'].get(
+                    'ping', 0) + 32)
 
     def _test_getnetworkinginfo(self):
         assert_equal(self.nodes[0].getnetworkinfo()['networkactive'], True)
```
