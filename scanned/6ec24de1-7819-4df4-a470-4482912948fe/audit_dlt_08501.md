# [?] fix deprecated usage of panic (#8134)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2021-02-16
Source: https://github.com/paritytech/substrate/commit/fb1b15ca8c4187f7a1766909338ba64eef6dcb7e
Type: security-commit

## Details
fix deprecated usage of panic (#8134)

## Patch
### frame/executive/src/lib.rs
```diff
@@ -320,7 +320,7 @@ where
 	) {
 		extrinsics.into_iter().for_each(|e| if let Err(e) = Self::apply_extrinsic(e) {
 			let err: &'static str = e.into();
-			panic!(err)
+			panic!("{}", err)
 		});
 
 		// post-extrinsics book-keeping
```

### frame/staking/reward-curve/src/lib.rs
```diff
@@ -353,13 +353,13 @@ fn generate_piecewise_linear(points: Vec<(u32, u32)>) -> TokenStream2 {
 		.unwrap_or(1_000_000_000);
 
 	for (x, y) in points {
-		let error = || panic!(format!(
+		let error = || panic!(
 			"Generated reward curve approximation doesn't fit into [0, 1] -> [0, 1] \
 			because of point:
 			x = {:07} per million
 			y = {:07} per million",
 			x, y
-		));
+		);
 
 		let x_perbill = x.checked_mul(1_000).unwrap_or_else(error);
 		let y_perbill = y.checked_mul(1_000).unwrap_or_else(error);
```

### primitives/core/src/crypto.rs
```diff
@@ -224,7 +224,7 @@ pub enum PublicError {
 
 /// Key that can be encoded to/from SS58.
 ///
-/// See https://github.com/paritytech/substrate/wiki/External-Address-Format-(SS58)#address-type
+/// See <https://github.com/paritytech/substrate/wiki/External-Address-Format-(SS58)#address-type>
 /// for information on the codec.
 #[cfg(feature = "full_crypto")]
 pub trait Ss58Codec: Sized + AsMut<[u8]> + AsRef<[u8]> + Default {
```

### primitives/core/src/hashing.rs
```diff
@@ -18,7 +18,7 @@
 //! Hashing functions.
 //!
 //! This module is gated by `full-crypto` feature. If you intend to use any of the functions
-//! defined here within your runtime, you should most likely rather use [sp_io::hashing] instead,
+//! defined here within your runtime, you should most likely rather use `sp_io::hashing` instead,
 //! unless you know what you're doing. Using `sp_io` will be more performant, since instead of
 //! computing the hash in WASM it delegates that computation to the host client.
 
```

### primitives/inherents/src/lib.rs
```diff
@@ -424,7 +424,7 @@ pub trait ProvideInherent {
 	/// - `Err(_)` indicates that this function failed and further operations should be aborted.
 	///
 	/// CAUTION: This check has a bug when used in pallets that also provide unsigned transactions.
-	/// See https://github.com/paritytech/substrate/issues/6243 for details.
+	/// See <https://github.com/paritytech/substrate/issues/6243> for details.
 	fn is_inherent_required(_: &InherentData) -> Result<Option<Self::Error>, Self::Error> { Ok(None) }
 
 	/// Check whether the given inherent is valid. Checking the inherent is optional and can be
```
