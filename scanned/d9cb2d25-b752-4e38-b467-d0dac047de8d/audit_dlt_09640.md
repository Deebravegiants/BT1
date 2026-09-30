# [?] merge bitcoin#26275: Fix crash on deriveaddresses when index is 2147483647 (2^31-1)

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2022-10-06
Source: https://github.com/dashpay/dash/commit/0b6839fb3a0bc1542b025d118786719be1b7041d
Type: security-commit

## Details
merge bitcoin#26275: Fix crash on deriveaddresses when index is 2147483647 (2^31-1)

## Patch
### src/rpc/misc.cpp
```diff
@@ -450,7 +450,7 @@ static RPCHelpMan deriveaddresses()
 
     UniValue addresses(UniValue::VARR);
 
-    for (int i = range_begin; i <= range_end; ++i) {
+    for (int64_t i = range_begin; i <= range_end; ++i) {
         FlatSigningProvider provider;
         std::vector<CScript> scripts;
         if (!desc->Expand(i, key_provider, scripts, provider)) {
```

### test/functional/rpc_deriveaddresses.py
```diff
@@ -44,6 +44,13 @@ def run_test(self):
         combo_descriptor = descsum_create("combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/0)")
         assert_equal(self.nodes[0].deriveaddresses(combo_descriptor), ["yZTyMdEJjZWJi6CwY6g3WurLESH3UsWrrM", "yZTyMdEJjZWJi6CwY6g3WurLESH3UsWrrM", "93EpXofs6W7eNiuj4gu2LJh8L8opowW1jz"])
 
+        # Before #26275, bitcoind would crash when deriveaddresses was
+        # called with derivation index 2147483647, which is the maximum
+        # positive value of a signed int32, and - currently - the
+        # maximum value that the deriveaddresses bitcoin RPC call
+        # accepts as derivation index.
+        assert_equal(self.nodes[0].deriveaddresses(descsum_create("pkh(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/1/1/*)"), [2147483647, 2147483647]), ["yUQ4ms3snAAXkWF1AzfnYrxAxgmNVhrydU"])
+
         hardened_without_privkey_descriptor = descsum_create("pkh(tpubD6NzVbkrYhZ4WaWSyoBvQwbpLkojyoTZPRsgXELWz3Popb3qkjcJyJUGLnL4qHHoQvao8ESaAstxYSnhyswJ76uZPStJRJCTKvosUCJZL5B/1'/1/0)")
         assert_raises_rpc_error(-5, "Cannot derive script without private keys", self.nodes[0].deriveaddresses, hardened_without_privkey_descriptor)
 
```
