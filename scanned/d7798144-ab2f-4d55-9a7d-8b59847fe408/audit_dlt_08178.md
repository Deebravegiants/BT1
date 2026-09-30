# [?] Fixes a panic (#8928)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2024-10-10
Source: https://github.com/ZcashFoundation/zebra/commit/fea9f46fbb199f2eb7d5c798f21ffb4f316c5d25
Type: security-commit

## Details
Fixes a panic (#8928)

## Patch
### zebra-chain/src/parameters/network/testnet.rs
```diff
@@ -89,6 +89,14 @@ pub struct ConfiguredFundingStreams {
 }
 
 impl ConfiguredFundingStreams {
+    /// Returns an empty [`ConfiguredFundingStreams`].
+    fn empty() -> Self {
+        Self {
+            height_range: None,
+            recipients: Some(Vec::new()),
+        }
+    }
+
     /// Converts a [`ConfiguredFundingStreams`] to a [`FundingStreams`], using the provided default values
     /// if `height_range` or `recipients` are None.
     fn convert_with_default(
@@ -601,10 +609,10 @@ impl Parameters {
             .with_halving_interval(PRE_BLOSSOM_REGTEST_HALVING_INTERVAL);
 
         // TODO: Always clear funding streams on Regtest once the testnet parameters are being serialized (#8920).
-        #[cfg(not(any(test, feature = "proptest-impl")))]
+        // #[cfg(not(any(test, feature = "proptest-impl")))]
         let parameters = parameters
-            .with_pre_nu6_funding_streams(ConfiguredFundingStreams::default())
-            .with_post_nu6_funding_streams(ConfiguredFundingStreams::default());
+            .with_pre_nu6_funding_streams(ConfiguredFundingStreams::empty())
+            .with_post_nu6_funding_streams(ConfiguredFundingStreams::empty());
 
         Self {
             network_name: "Regtest".to_string(),
```
