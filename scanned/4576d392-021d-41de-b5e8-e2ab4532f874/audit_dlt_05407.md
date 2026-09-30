# [?] Merge #19756: tests: add sync_all to fix race condition in wallet groups test

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2020-08-18
Source: https://github.com/litecoin-project/litecoin/commit/e6e277f9ed4da7aff9b7b39a7838bada0c3e572a
Type: security-commit

## Details
Merge #19756: tests: add sync_all to fix race condition in wallet groups test

72ae20fc142457a200278cb2fedc5e32a3766b58 tests: add sync_all to fix race condition in wallet groups test (Karl-Johan Alm)

Pull request description:

  This most likely fixes #19749, the intermittent CI issues with wallet_groups.

  This fix is also included in #19743.

Top commit has no ACKs.

Tree-SHA512: dd6ef7f89829483e2278191c21fe0912b51fd2187c10a0fa158339c5ab9f22d93b733ae10f17ef25d8b64f44e596e66dba8d7db5c009343472f422ce4cd67d8f

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
