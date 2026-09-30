# [?] trustedcoin: billing_index: mitigate against CPU DOS from malicious server

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2026-08-07
Source: https://github.com/spesmilo/electrum/commit/fba8180c873dd0b258558801d8d951a0355c622a
Type: security-commit

## Details
trustedcoin: billing_index: mitigate against CPU DOS from malicious server

## Patch
### electrum/plugins/trustedcoin/trustedcoin.py
```diff
@@ -366,6 +366,8 @@ def add_new_billing_address(self, billing_index: int, address: str, addr_type: s
                 raise Exception('trustedcoin billing address inconsistency.. '
                                 'for index {}, already saved {}, now got {}'
                                 .format(billing_index, saved_addr, address))
+        if billing_index > 50_000:  # otherwise DOS against CPU/memory/disk
+            raise Exception(f"trustedcoin billing_index too high. got {billing_index} > 50_000")
         # do we have all prior indices? (are we synced?)
         largest_index_we_have = max(billing_addresses_of_this_type) if billing_addresses_of_this_type else -1
         if largest_index_we_have + 1 < billing_index:  # need to sync
```
