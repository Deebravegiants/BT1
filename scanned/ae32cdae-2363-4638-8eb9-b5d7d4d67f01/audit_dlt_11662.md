# [?] Merge rust-bitcoin/rust-bitcoin#3667: Fix psbt fuzz crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2024-11-28
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/a22dfc2897d71041e81a3fe260ae31c09267e223
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#3667: Fix psbt fuzz crash

9aebb96fb99e8e9e019663659c6eff851a62f2ce Fix psbt fuzz crash (Sanket Kanjalkar)

Pull request description:

  Fixes: https://github.com/rust-bitcoin/rust-bitcoin/issues/3628

  This occurs when combining two PSBTs with different xpub key sources. Added a length check before indexing into slices to prevent out-of-bounds access.

  For some reason, the precommit hook complained about non-ascii files. I don't think any of the names here are non-ascii

ACKs for top commit:
  apoelstra:
    ACK 9aebb96fb99e8e9e019663659c6eff851a62f2ce; successfully ran local tests; thanks!
  tcharding:
    ACK 9aebb96fb99e8e9e019663659c6eff851a62f2ce

Tree-SHA512: b61274c594bc1f2ea4d04c8a7ace673a7632bb9ea31f59b56779a008c35e61281ea4f6b869990d886779e3e556932a3b2e8b015733ef18e236f12ca77e211c26

## Patch
### bitcoin/src/psbt/mod.rs
```diff
@@ -255,8 +255,9 @@ impl Psbt {
                                 == derivation2[derivation2.len() - derivation1.len()..])
                     {
                         continue;
-                    } else if derivation2[..]
-                        == derivation1[derivation1.len() - derivation2.len()..]
+                    } else if derivation2.len() <= derivation1.len()
+                        && derivation2[..]
+                                == derivation1[derivation1.len() - derivation2.len()..]
                     {
                         entry.insert((fingerprint1, derivation1));
                         continue;
@@ -2116,6 +2117,16 @@ mod tests {
         assert_eq!(psbt1, psbt2);
     }
 
+
+    // https://github.com/rust-bitcoin/rust-bitcoin/issues/3628
+    #[test]
+    fn test_combine_psbt_fuzz_3628() {
+        let mut psbt1 = hex_psbt(include_str!("../../tests/data/psbt_fuzz1.hex")).unwrap();
+        let psbt2 = hex_psbt(include_str!("../../tests/data/psbt_fuzz2.hex")).unwrap();
+
+        assert!(matches!(psbt1.combine(psbt2).unwrap_err(), Error::CombineInconsistentKeySources(_)));
+    }
+
     #[cfg(feature = "rand-std")]
     fn gen_keys() -> (PrivateKey, PublicKey, Secp256k1<All>) {
         use secp256k1::rand::thread_rng;
```

### bitcoin/tests/data/psbt_fuzz1.hex
```diff
@@ -0,0 +1 @@
+70736274ff01000a000000ff0000000074ff4f010488b21eff02000001004a92244992244902030203030303030303030303030303030303030303030303030303030303030303f4000000000000000a000208ffffffff08080804000000000000000c080808000b0000000000010000
\ No newline at end of file
```

### bitcoin/tests/data/psbt_fuzz2.hex
```diff
@@ -0,0 +1 @@
+70736274ff01000a000000ff0000000074ff4f010488b21eff02000001004a92244992244902030203030303030303030303030303030303030303030303030303030303030303f4000000000000000a000208ffffffff080808040000000000000008000000000000001000
\ No newline at end of file
```
