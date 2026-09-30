# [?] Fix nondeterministic test failure in wallet_listreceivedby.py

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2022-02-08
Source: https://github.com/zcash/zcash/commit/3f840676582ecb41561ea10917e3db0f36c0eacc
Type: security-commit

## Details
Fix nondeterministic test failure in wallet_listreceivedby.py

## Patch
### qa/rpc-tests/wallet_listreceived.py
```diff
@@ -107,15 +107,16 @@ def test_received_sprout(self, height):
         # Confirm transaction (10 ZEC shielded)
         self.generate_and_sync(height+3)
 
-        # adjust confirmations
-        r[0]['confirmations'] = 1
-        # adjust blockindex
-        r[0]['blockindex'] = 1
-        # adjust height
-        r[0]['blockheight'] = height + 3
-
         # Require one confirmation, note should be present
-        assert_equal(r, self.nodes[1].z_listreceivedbyaddress(zaddr1))
+        r0 = self.nodes[1].z_listreceivedbyaddress(zaddr1)
+        assert_equal(1, len(r0), "Should have received one (unconfirmed) note")
+        assert_equal(txid_shielding1, r0[0]['txid'])
+        assert_equal(10, r0[0]['amount'])
+        assert_equal(1000000000, r0[0]['amountZat'])
+        assert_false(r0[0]['change'], "Note should not be change")
+        assert_equal(no_memo, r0[0]['memo'])
+        assert_equal(1, r0[0]['confirmations'])
+        assert_equal(height + 3, r0[0]['blockheight'])
 
         taddr = self.nodes[1].getnewaddress()
         # Generate some change by sending part of zaddr1 back to taddr
```
