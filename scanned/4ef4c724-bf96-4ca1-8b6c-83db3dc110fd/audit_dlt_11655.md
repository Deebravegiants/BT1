# [?] Merge rust-bitcoin/rust-bitcoin#4984: fix function name in panic message for chain_hash_and_genesis_block

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-09-15
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/2c4a73d0c428148b82d65f5394ecee62983cda35
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#4984: fix function name in panic message for chain_hash_and_genesis_block

77d326627e44d9f04efd1551e2c0e155b7b6f546 fix function name in panic message for chain_hash_and_genesis_block (Bugar)

Pull request description:

  Correct the function name reference in the panic message 
  from `chain_hash_genesis_block` to `chain_hash_and_genesis_block` to match the actual function name


ACKs for top commit:
  apoelstra:
    ACK 77d326627e44d9f04efd1551e2c0e155b7b6f546; successfully ran local tests


Tree-SHA512: c81d06c1160c311a36bbc88f6166fcd118ec0f6b272d1e5645577247fd17774ef4fb1f3615d57ca10e58b8415786882097f7eb5e72c86008bd84e188ff0cd4c8

## Patch
### bitcoin/src/blockdata/constants.rs
```diff
@@ -388,7 +388,7 @@ mod test {
             Network::Testnet(TestnetVersion::V4) => {},
             Network::Signet => {},
             Network::Regtest => {},
-            _ => panic!("update ChainHash::using_genesis_block and chain_hash_genesis_block with new variants"),
+            _ => panic!("update ChainHash::using_genesis_block and chain_hash_and_genesis_block with new variants"),
         }
     }
 
```
