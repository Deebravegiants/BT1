# [?] [genesis] prevent race condition in setting owner account

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2020-09-18
Source: https://github.com/move-language/move/commit/bb9224aef0b3c39d23dc39c66673e9f4b124b969
Type: security-commit

## Details
[genesis] prevent race condition in setting owner account

Closes: #6097

## Patch
### config/management/genesis/src/key.rs
```diff
@@ -98,10 +98,7 @@ pub struct OwnerKey {
 
 impl OwnerKey {
     pub fn execute(self) -> Result<Ed25519PublicKey, Error> {
-        self.key.submit_key(
-            libra_global_constants::OWNER_KEY,
-            Some(libra_global_constants::OWNER_ACCOUNT),
-        )
+        self.key.submit_key(libra_global_constants::OWNER_KEY, None)
     }
 }
 
```
