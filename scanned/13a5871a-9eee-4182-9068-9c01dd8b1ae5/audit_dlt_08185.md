# [?] fix rust beta panic string warnings (#1731)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2021-02-14
Source: https://github.com/ZcashFoundation/zebra/commit/21dbf5cb69c355a5148f388cd9eacf48675adeb6
Type: security-commit

## Details
fix rust beta panic string warnings (#1731)

## Patch
### zebra-chain/src/sprout/address.rs
```diff
@@ -74,9 +74,7 @@ impl ZcashDeserialize for SproutShieldedAddress {
         let network = match version_bytes {
             magics::MAINNET => Network::Mainnet,
             magics::TESTNET => Network::Testnet,
-            _ => panic!(SerializationError::Parse(
-                "bad sprout shielded addr version/type",
-            )),
+            _ => panic!("SerializationError: bad sprout shielded addr version/type"),
         };
 
         Ok(SproutShieldedAddress {
```

### zebra-chain/src/sprout/keys.rs
```diff
@@ -89,9 +89,7 @@ impl ZcashDeserialize for SpendingKey {
         let network = match version_bytes {
             sk_magics::MAINNET => Network::Mainnet,
             sk_magics::TESTNET => Network::Testnet,
-            _ => panic!(SerializationError::Parse(
-                "bad sprout spending key version/type",
-            )),
+            _ => panic!("SerializationError: bad sprout spending key version/type"),
         };
 
         Ok(SpendingKey {
@@ -277,9 +275,7 @@ impl ZcashDeserialize for IncomingViewingKey {
         let network = match version_bytes {
             ivk_magics::MAINNET => Network::Mainnet,
             ivk_magics::TESTNET => Network::Testnet,
-            _ => panic!(SerializationError::Parse(
-                "bad sprout incoming viewing key network",
-            )),
+            _ => panic!("SerializationError: bad sprout incoming viewing key network"),
         };
 
         Ok(IncomingViewingKey {
```

### zebra-chain/src/work/difficulty.rs
```diff
@@ -364,16 +364,15 @@ impl ExpandedDifficulty {
         // This assertion also makes sure that size fits in its 8 bit compact field
         assert!(
             size < (31 + OFFSET) as _,
-            format!(
-                "256^size (256^{}) must fit in a u256, after the sign bit adjustment and offset",
-                size
-            )
+            "256^size (256^{}) must fit in a u256, after the sign bit adjustment and offset",
+            size
         );
         let size = u32::try_from(size).expect("a 0-6 bit value fits in a u32");
 
         assert!(
             mantissa <= UNSIGNED_MANTISSA_MASK.into(),
-            format!("mantissa {:x?} must fit in its compact field", mantissa)
+            "mantissa {:x?} must fit in its compact field",
+            mantissa
         );
         let mantissa = u32::try_from(mantissa).expect("a 0-23 bit value fits in a u32");
 
```

### zebra-state/src/tests.rs
```diff
@@ -151,10 +151,10 @@ fn test_block_locator_heights() {
             "locators must end with the specified final height"
         );
         assert!(height - final_height.0 <= constants::MAX_BLOCK_REORG_HEIGHT,
-                    format!("locator for {} must not be more than the maximum reorg height {} below the tip, but {} is {} blocks below the tip",
-                         height,
-                         constants::MAX_BLOCK_REORG_HEIGHT,
-                         final_height.0,
-                         height - final_height.0));
+                    "locator for {} must not be more than the maximum reorg height {} below the tip, but {} is {} blocks below the tip",
+                    height,
+                    constants::MAX_BLOCK_REORG_HEIGHT,
+                    final_height.0,
+                    height - final_height.0);
     }
 }
```
