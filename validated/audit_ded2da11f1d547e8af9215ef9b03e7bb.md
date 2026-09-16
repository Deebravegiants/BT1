Now confirmed: `on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs` is invoked by `pallet-ismp`'s router when a cross-chain `PostRequest` targeting the HFT module ID is delivered — reachable by any relayer/token bridger relaying a message from a registered (but otherwise arbitrary-content) source contract on any connected chain. The `body` is ABI-decoded into a `Message`, and its `data` field (fully attacker-controlled calldata) is SCALE-decoded twice: once into `SubstrateCalldata`, and then its `runtime_call: Vec<u8>` field is decoded straight into `T::RuntimeCall` via plain `Decode::decode` at line 189, with **no recursion-depth limit**. [1](#0-0) [2](#0-1) 

### Title
Unbounded-recursion SCALE deserialization of untrusted cross-chain calldata in `pallet-hyper-fungible-token` - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`pallet-hyper-fungible-token::on_accept` decodes the attacker-supplied `calldata` field of a cross-chain token-transfer message into a `T::RuntimeCall` using plain `Decode::decode`, with no depth/recursion limit, unlike the sibling `pallet-call-decompressor` which was specifically hardened against this exact class of bug.

### Finding Description
`on_accept` is the `IsmpModule` entrypoint invoked whenever `pallet-ismp` routes an incoming `PostRequest` addressed to the HFT module ID; this is triggered by any relayer submitting a message that originated from a registered source-chain HFT/WrappedHFT contract [3](#0-2) . After minting/transferring tokens, if `message.data` (the ABI `bytes data` field, fully controlled by whoever calls `send`/bridges tokens on the source chain) is non-empty, it is decoded into `SubstrateCalldata` and then `substrate_data.runtime_call` is decoded directly into the runtime's `RuntimeCall` enum with `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` [4](#0-3) .

`RuntimeCall` is a deeply nested, recursive enum (calls that box further calls, e.g. `Sudo::sudo { call: Box<RuntimeCall> }`, `Utility::batch { calls: Vec<RuntimeCall> }`, etc.). SCALE's derive-generated `Decode` implementation recurses once per nesting level with no bound, so an attacker can supply a byte string encoding thousands of nested call variants and drive the decoder into unbounded stack recursion, crashing the executing process (stack overflow is an unrecoverable abort in Rust, not a catchable panic).

This exact vulnerability class was already identified and fixed elsewhere in this same codebase: `pallet-call-decompressor` now uses `T::RuntimeCall::decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)` in both its dispatch and `validate_unsigned` paths specifically to prevent this [5](#0-4) , and the associated test `decompress_stack_exhaustion_poc` demonstrates the crafted-nested-call attack pattern [6](#0-5) . `pallet-hyper-fungible-token`'s calldata-execution feature (documented publicly) never received the equivalent hardening.

### Impact Explanation
A successful stack-overflow abort during on-chain message execution (inside `on_accept`, called from `pallet-ismp`'s `handle_unsigned`/`handle` message-processing path) crashes the node process executing that block. Because every collator/validator processing the same block hits the identical crafted payload, this is a deterministic, network-wide liveness failure — a token bridger can render the destination chain (or the relevant parachain/runtime) unable to finalize blocks, i.e. "a route unable to deliver messages," satisfying the Validate criteria. This is reachable by anyone able to trigger a cross-chain HFT transfer with attached calldata — no privileged role required.

### Likelihood Explanation
High. Triggering it only requires calling the registered source-chain `HyperFungibleToken`/`WrappedHyperFungibleToken` contract's send function with a crafted `data` payload (any address can do this, the transfer itself can be of a trivial/dust amount) and having a relayer deliver the resulting `PostRequest` — a permissionless action integral to normal bridge operation.

### Recommendation
Replace the plain `T::RuntimeCall::decode(...)` call in `on_accept` with `T::RuntimeCall::decode_all_with_depth_limit(MAX_DEPTH, ...)`, mirroring the fix already applied in `pallet-call-decompressor`, and apply the same bound to the `SubstrateCalldata::decode` and `MultiSignature::decode` calls that consume the same untrusted `message.data` bytes.

### Proof of Concept
1. On the source EVM chain, call the `HyperFungibleToken` contract's transfer/send function with a minimal token amount and `data` set to a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <bytes> }` where `<bytes>` encodes thousands of nested `RuntimeCall::Sudo(Box<RuntimeCall::Sudo(Box<...>)>)` (or any other Box/Vec-of-`RuntimeCall`-containing dispatchable available in the destination runtime), following the same construction as `decompress_stack_exhaustion_poc` [7](#0-6) .
2. Have a relayer submit the resulting cross-chain `PostRequest` to the destination chain via `pallet-ismp`.
3. When `pallet-hyper-fungible-token::on_accept` reaches `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` [4](#0-3) , the unbounded recursive decode exhausts the call stack and aborts the executing node process, instead of returning `HftError::RuntimeCallDecodeError` as intended by the depth-limited design used elsewhere in the codebase.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-59)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-122)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-196)
```rust
			let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
				.map_err(HftError::RuntimeCallDecodeError)?;
			// Apply the runtime's base call filter so that cross-chain calls cannot
			// reach dispatchables that the runtime has otherwise filtered out (e.g.
			// during a maintenance mode or a SafeMode period).
			if !<T as frame_system::Config>::BaseCallFilter::contains(&runtime_call) {
				Err(HftError::CallFiltered)?
			}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L256-268)
```rust
	/// Decodes and executes the encoded runtime call represented in bytes.
	///
	/// Decoding fails if any bytes are left in the input after the runtime
	/// call is read. This is what catches a compressed payload whose decoded
	/// contents are a valid call followed by padding.
	///
	/// - `call_bytes`: the uncompressed encoded runtime call.
	pub fn decode_and_execute(call_bytes: Vec<u8>) -> DispatchResult {
		let runtime_call = <T as frame_system::Config>::RuntimeCall::decode_all_with_depth_limit(
			MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
			&mut &call_bytes[..],
		)
		.map_err(|_| Error::<T>::ErrorDecodingCall)?;
```

**File:** modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs (L313-352)
```rust
#[test]
fn decompress_stack_exhaustion_poc() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		use crate::runtime::RuntimeCall;
		use codec::Encode;

		let inner_call = RuntimeCall::System(frame_system::Call::remark { remark: Vec::new() });

		let mut nested_calls =
			RuntimeCall::Sudo(pallet_sudo::Call::sudo { call: Box::new(inner_call) });

		for _ in 1..1000 {
			nested_calls =
				RuntimeCall::Sudo(pallet_sudo::Call::sudo { call: Box::new(nested_calls) });
		}

		let encoded = nested_calls.encode();
		let mut buffer = vec![0u8; 1000000];
		let compressed = zstd_safe::compress(&mut buffer[..], encoded.as_slice(), 3).unwrap();
		let final_compressed_call = buffer[..compressed].to_vec();

		let res = pallet_call_decompressor::Pallet::<Test>::decompress_call(
			RuntimeOrigin::none(),
			final_compressed_call.to_vec(),
			encoded.len() as u32,
		)
		.err()
		.unwrap();

		assert_eq!(
			res,
			DispatchError::Module(ModuleError {
				index: 10,
				error: [3, 0, 0, 0],
				message: Some("ErrorDecodingCall")
			})
		);
	});
}
```
