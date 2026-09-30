# [?] tests: add sync_all to fix race condition in wallet groups test

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-08-18
Source: https://github.com/litecoin-project/litecoin/commit/72ae20fc142457a200278cb2fedc5e32a3766b58
Type: security-commit

## Details
tests: add sync_all to fix race condition in wallet groups test

## Patch
### test/functional/wallet_groups.py
```diff
@@ -103,6 +103,7 @@ def run_test(self):
         self.nodes[0].sendtoaddress(addr_aps, 1.0)
         self.nodes[0].sendtoaddress(addr_aps, 1.0)
         self.nodes[0].generate(1)
+        self.sync_all()
         txid4 = self.nodes[3].sendtoaddress(self.nodes[0].getnewaddress(), 0.1)
         tx4 = self.nodes[3].getrawtransaction(txid4, True)
         # tx4 should have 2 inputs and 2 outputs although one output would
```
