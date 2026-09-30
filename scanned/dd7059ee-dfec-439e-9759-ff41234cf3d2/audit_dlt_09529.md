# [?] Merge pull request #580 from chainflip-io/fix/out-of-bounds-signature

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2021-09-28
Source: https://github.com/chainflip-io/chainflip-backend/commit/773d4ea0f9257d7bbcb8e72cddcb803894325ead
Type: security-commit

## Details
Merge pull request #580 from chainflip-io/fix/out-of-bounds-signature

Fix out of bounds signature bug

## Patch
### engine/src/signing/client/client_inner/client_inner.rs
```diff
@@ -49,7 +49,7 @@ impl From<SchnorrSignature> for pallet_cf_vaults::SchnorrSigTruncPubkey {
         // Take the Keccak-256 hash of the public key. You should now have a string that is 64 characters / 32 bytes. (note: SHA3-256 eventually became the standard, but Ethereum uses Keccak)
         let hash = Keccak256::hash(&cfe_sig.r.serialize_uncompressed()).0;
         // Take the last 40 characters / 20 bytes of this public key (Keccak-256). Or, in other words, drop the first 24 characters / 12 bytes. These 40 characters / 20 bytes are the address. When prefixed with 0x it becomes 42 characters long.
-        let eth_pub_key: [u8; 20] = hash[12..=32].try_into().expect("Is valid pubkey");
+        let eth_pub_key: [u8; 20] = hash[12..].try_into().expect("Is valid pubkey");
         Self {
             s: cfe_sig.s,
             eth_pub_key,
```
