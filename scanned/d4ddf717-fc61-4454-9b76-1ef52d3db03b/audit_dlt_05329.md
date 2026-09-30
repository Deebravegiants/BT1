# [?] Fix an interger overflow in message_proof when looking beyond genesis (#1392)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2023-10-03
Source: https://github.com/FuelLabs/fuel-core/commit/d0e48baf46ae96f3da7b9abedf07c5e766e8c1bb
Type: security-commit

## Details
Fix an interger overflow in message_proof when looking beyond genesis (#1392)

Fixes https://github.com/FuelLabs/fuel-core/issues/1334

See https://github.com/FuelLabs/fuel-vm/pull/596 for follow-up work.

---------

Co-authored-by: Green Baneling <XgreenX9999@gmail.com>
Co-authored-by: Brandon Vrooman <brandon.vrooman@fuel.sh>

## Patch
### CHANGELOG.md
```diff
@@ -40,6 +40,7 @@ Description of the upcoming release here.
 - [#1342](https://github.com/FuelLabs/fuel-core/pull/1342): Add error handling for P2P requests to return `None` to requester and log error.
 - [#1383](https://github.com/FuelLabs/fuel-core/pull/1383): Disallow usage of `log` crate internally in favor of `tracing` crate.
 - [#1390](https://github.com/FuelLabs/fuel-core/pull/1390): Up the `ethers` version to `2` to fix an issue with `tungstenite`.
+- [#1392](https://github.com/FuelLabs/fuel-core/pull/1392): Fixed an overflow in `message_proof`.
 - [#1393](https://github.com/FuelLabs/fuel-core/pull/1393): Increase heartbeat timeout from `2` to `60` seconds, as suggested in [this issue](https://github.com/FuelLabs/fuel-core/issues/1330).
 
 #### Breaking
```

### crates/fuel-core/src/query/message.rs
```diff
@@ -205,7 +205,12 @@ pub fn message_proof<T: MessageProofData + ?Sized>(
         None => return Ok(None),
     };
 
-    let verifiable_commit_block_height = *commit_block_header.height() - 1u32.into();
+    let block_height = *commit_block_header.height();
+    if block_height == 0u32.into() {
+        // Cannot look beyond the genesis block
+        return Ok(None)
+    }
+    let verifiable_commit_block_height = block_height - 1u32.into();
     let block_proof = database.block_history_proof(
         message_block_header.height(),
         &verifiable_commit_block_height,
```
