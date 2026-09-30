# [?] Avoid Panic When Fetching Info Before Bridge is Initialized (#504)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2020-11-19
Source: https://github.com/paritytech/polkadot-sdk/commit/e91cab68d45461bb1bedbf2562b11fdcab2ce061
Type: security-commit

## Details
Avoid Panic When Fetching Info Before Bridge is Initialized (#504)

* Allow bridge pallet to return no finalized headers

* Update Runtime APIs to optionally return best finalized header

* Update relay to handle optional best finalized headers

* Fix Clippy lints

* Return a dummy header instead of an Option

* Remove Option from runtime Apis

* Remove support for handling optional finalized headers in relay

## Patch
### bridges/modules/substrate/src/lib.rs
```diff
@@ -289,6 +289,9 @@ impl<T: Trait> Module<T> {
 
 	/// Get the best finalized header the pallet knows of.
 	///
+	/// Returns a dummy header if there is no best header. This can only happen
+	/// if the pallet has not been initialized yet.
+	///
 	/// Since this has been finalized correctly a user of the bridge
 	/// pallet should be confident that any transactions that were
 	/// included in this or any previous header will not be reverted.
@@ -424,6 +427,9 @@ pub trait BridgeStorage {
 	fn best_headers(&self) -> Vec<HeaderId<Self::Header>>;
 
 	/// Get the best finalized header the pallet knows of.
+	///
+	/// Returns None if there is no best header. This can only happen if the pallet
+	/// has not been initialized yet.
 	fn best_finalized_header(&self) -> ImportedHeader<Self::Header>;
 
 	/// Update the best finalized header the pallet knows of.
@@ -525,9 +531,22 @@ impl<T: Trait> BridgeStorage for PalletStorage<T> {
 	}
 
 	fn best_finalized_header(&self) -> ImportedHeader<BridgedHeader<T>> {
+		// We will only construct a dummy header if the pallet is not initialized and someone tries
+		// to use the public module interface (not dispatchables) to get the best finalized header.
+		// This is an edge case since this can only really happen when bootstrapping the bridge.
 		let hash = <BestFinalized<T>>::get();
-		self.header_by_hash(hash)
-			.expect("A finalized header was added at genesis, therefore this must always exist")
+		self.header_by_hash(hash).unwrap_or_else(|| ImportedHeader {
+			header: <BridgedHeader<T>>::new(
+				Default::default(),
+				Default::default(),
+				Default::default(),
+				Default::default(),
+				Default::default(),
+			),
+			requires_justification: false,
+			is_finalized: false,
+			signal_hash: None,
+		})
 	}
 
 	fn update_best_finalized(&self, hash: BridgedBlockHash<T>) {
@@ -620,6 +639,9 @@ mod tests {
 				is_halted: false,
 			};
 
+			assert!(Module::<TestRuntime>::best_headers().is_empty());
+			assert_eq!(Module::<TestRuntime>::best_finalized(), test_header(0));
+
 			assert_ok!(Module::<TestRuntime>::initialize(Origin::root(), init_data.clone()));
 
 			let storage = PalletStorage::<TestRuntime>::new();
```

### bridges/relays/substrate-client/src/error.rs
```diff
@@ -34,6 +34,8 @@ pub enum Error {
 	Request(RequestError),
 	/// The response from the server could not be SCALE decoded.
 	ResponseParseFailed(codec::Error),
+	/// The Substrate bridge pallet has not yet been initialized.
+	UninitializedBridgePallet,
 	/// Account does not exist on the chain.
 	AccountDoesNotExist,
 	/// Custom logic error.
@@ -70,6 +72,7 @@ impl ToString for Error {
 			Self::WsConnectionError(e) => e.to_string(),
 			Self::Request(e) => e.to_string(),
 			Self::ResponseParseFailed(e) => e.what().to_string(),
+			Self::UninitializedBridgePallet => "The Substrate bridge pallet has not been initialized yet.".into(),
 			Self::AccountDoesNotExist => "Account does not exist on the chain".into(),
 			Self::Custom(e) => e.clone(),
 		}
```

### bridges/relays/substrate/src/headers_target.rs
```diff
@@ -91,13 +91,12 @@ where
 		let decoded_response: Vec<(P::Number, P::Hash)> =
 			Decode::decode(&mut &encoded_response.0[..]).map_err(SubstrateError::ResponseParseFailed)?;
 
-		const WARNING_MSG: &str = "Parsed an empty list of headers, we should always have at least
-									one. Has the bridge pallet been initialized yet?";
-		let best_header = decoded_response
+		// If we parse an empty list of headers it means that bridge pallet has not been initalized
+		// yet. Otherwise we expect to always have at least one header.
+		decoded_response
 			.last()
-			.ok_or_else(|| SubstrateError::ResponseParseFailed(WARNING_MSG.into()))?;
-		let best_header_id = HeaderId(best_header.0, best_header.1);
-		Ok(best_header_id)
+			.ok_or(SubstrateError::UninitializedBridgePallet)
+			.map(|(num, hash)| HeaderId(*num, *hash))
 	}
 
 	async fn is_known_header(&self, id: HeaderIdOf<P>) -> Result<(HeaderIdOf<P>, bool), Self::Error> {
```
