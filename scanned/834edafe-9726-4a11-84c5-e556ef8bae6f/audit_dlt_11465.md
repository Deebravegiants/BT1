# [?] fix(eth-on-near-client): Overflow in rust-ethash (#486)

## Summary
Severity: Unknown
Chain: Bridge
Component: Near-One/rainbow-bridge
Published: 2021-02-08
Source: https://github.com/Near-One/rainbow-bridge/commit/45bcab9344aadf77c4a45b9c1e472bc3c627c835
Type: security-commit

## Details
fix(eth-on-near-client): Overflow in rust-ethash (#486)

Fix #460

## Patch
### contracts/near/Cargo.lock
```diff
@@ -727,7 +727,7 @@ dependencies = [
 [[package]]
 name = "ethash"
 version = "0.4.0"
-source = "git+https://github.com/nearprotocol/rust-ethash?branch=upgrade-eth-types#d1dd3efad109498189c03957dc1cf80b4f410632"
+source = "git+https://github.com/nearprotocol/rust-ethash#ed163a30dfdd6b1b61a817de7ccb1b2224c8a431"
 dependencies = [
  "byteorder",
  "ethereum-types 0.9.2",
```

### contracts/near/eth-client/Cargo.toml
```diff
@@ -16,7 +16,7 @@ rlp = "0.4.2"
 futures = "0.1.26"
 primal = "0.2.3"
 arrutil = "0.1.2"
-ethash = { git = "https://github.com/nearprotocol/rust-ethash", branch = "upgrade-eth-types" }
+ethash = { git = "https://github.com/nearprotocol/rust-ethash" }
 hex = "0.4.0"
 rustc-hex = "2.1.0"
 
```

### contracts/near/eth-client/src/lib.rs
```diff
@@ -395,7 +395,7 @@ impl EthClient {
         let pair = ethash::hashimoto_with_hasher(
             header_hash.0,
             nonce.0,
-            ethash::get_full_size(header_number as usize / 30000),
+            ethash::get_full_size(header_number / 30000),
             |offset| {
                 let idx = *index.borrow_mut();
                 *index.borrow_mut() += 1;
```
