# [?] Prevent potential overflow in `TestBlockIterator`

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2023-02-28
Source: https://github.com/casper-network/casper-node/commit/4a56a7c514f1d9be83ca6d190a770c3364641647
Type: security-commit

## Details
Prevent potential overflow in `TestBlockIterator`

## Patch
### node/src/lib.rs
```diff
@@ -224,21 +224,7 @@ mod tests {
                         if switch_block_heights.contains(&self.block.height()) =>
                     {
                         let is_successor_of_switch_block =
-                            switch_block_heights.contains(&(self.block.height() - 1));
-
-                        // let secret_keys: Vec<SecretKey> = iter::repeat_with(|| {
-                        //     SecretKey::ed25519_from_bytes(
-                        //         self.rng.gen::<[u8; SecretKey::ED25519_LENGTH]>(),
-                        //     )
-                        //     .unwrap()
-                        // })
-                        // .take(4)
-                        // .collect();
-                        // let validators: BTreeMap<_, _> = secret_keys
-                        //     .iter()
-                        //     .map(|sk| (PublicKey::from(sk), 100.into()))
-                        //     .collect();
-
+                            switch_block_heights.contains(&(self.block.height().saturating_sub(1)));
                         (
                             true,
                             is_successor_of_switch_block,
```
