# [?] Fix panic on bad tx signature (#889)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2022-11-11
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/1c3c9a468751aa14d86b730da6ba549afe6ea862
Type: security-commit

## Details
Fix panic on bad tx signature (#889)

## Patch
### eth-types/src/geth_types.rs
```diff
@@ -206,7 +206,10 @@ impl Transaction {
             .to_vec()
             .try_into()
             .expect("hash length isn't 32 bytes");
-        let v = (self.v - 35 - chain_id * 2) as u8;
+        let v = self
+            .v
+            .checked_sub(35 + chain_id * 2)
+            .ok_or(Error::Signature(libsecp256k1::Error::InvalidSignature))? as u8;
         let pk = recover_pk(v, &self.r, &self.s, &msg_hash)?;
         // msg_hash = msg_hash % q
         let msg_hash = BigUint::from_bytes_be(msg_hash.as_slice());
```
