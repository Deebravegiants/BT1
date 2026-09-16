Confirmed the `hyper-fungible-token` pallet is wired into both `parachain/runtimes/gargantua` and `parachain/runtimes/nexus` (per `ismp.rs`/`lib.rs` matches), i.e. it runs alongside `pallet_sudo`/`pallet_utility` in a real `RuntimeCall` enum, so the recursive-call gadget demonstrated by `decompress_stack_exhaustion_poc` (nesting `Sudo::sudo{ call: Box<RuntimeCall> }` ~1000 times) is a shape `RuntimeCall::decode` will actually walk into.

### Title
Unbounded recursive SCALE-decode of untrusted cross-chain calldata causes stack-exhaustion DoS in `hyper-fungible-token` - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` decodes the untrusted `data` field of an incoming ISMP `PostRequest` into a `RuntimeCall` using plain `codec::Decode::decode`, with no recursion-depth bound, before dispatching it. Any counterparty contract configured via `ContractToAsset` can trigger this path with a single cross-chain token transfer.

### Finding Description
In `on_accept`, after minting/transferring the bridged asset, optional calldata is processed: [1](#0-0) 

and the embedded runtime call is decoded with an unbounded decoder: [2](#0-1) 

`T::RuntimeCall::decode` here is the plain `codec::Decode::decode`, not `decode_all_with_depth_limit`. The runtime's `RuntimeCall` enum is recursive through pallets such as `pallet_sudo::Call::sudo { call: Box<RuntimeCall> }` and `pallet_utility` batch calls, so an attacker-controlled byte string can encode thousands of nested `Box<RuntimeCall>` variants. Decoding such a value recurses once per nesting level and exhausts the call stack, aborting/crashing the node process handling the ISMP message.

This is the exact bug class the codebase itself has already fixed once, in `pallet-call-decompressor`, which deliberately switched to `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)` for the identical `RuntimeCall` decode and added a regression test proving the unbounded decoder crashes on deep `Sudo`-nesting: [3](#0-2) [4](#0-3) 

`hyper-fungible-token::on_accept`, which reaches an equivalent `T::RuntimeCall::decode` on attacker-supplied bytes, never received the analogous fix — it is the deserialization boundary the InspireMusic-style advisory (untrusted bytes deserialized straight into an executable structure, CWE-20/CWE-502) maps onto in this Rust/SCALE codebase. Rust's `codec::Decode` cannot achieve arbitrary code execution the way Python `pickle.load` can, but it can be driven to unbounded recursion, which is the concrete, reachable analog of "deserialization of untrusted data" causing uncontrolled resource consumption / crash.

### Impact Explanation
Any unprivileged actor able to originate a cross-chain `PostRequest` to a registered `HyperFungibleToken` contract (a normal bridge-token transfer with non-empty `data`) can crash/hang the destination parachain's block-execution worker, since `on_accept` runs inside `handle_incoming_message`/dispatch and a stack overflow there traps the runtime. This is a message-dispatch-reachable denial of service — halting delivery of all ISMP messages routed through the affected chain until the trigger is filtered/patched — which meets the "route unable to deliver messages" bar.

### Likelihood Explanation
Likelihood is high: the trigger requires only (1) a contract already mapped in `ContractToAsset` (a normal, expected bridge deployment, not an attacker-controlled precondition) and (2) crafting `message.data` as a SCALE-encoded `SubstrateCalldata` whose `runtime_call` field is a deeply nested `Sudo`/`Utility` call. No signature or special privilege is needed for the unsigned-recursion path itself — the decode happens before the (optional) signature check even runs, since decoding is only reached inside the `if !message.data.is_empty()` branch and the signature check operates on the already-decoded `substrate_data`, but the recursive decode of `substrate_data.runtime_call` at line 189 happens regardless of whether a signature is present.

### Recommendation
Replace `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` with a depth-limited decode, mirroring the fix already applied in `pallet-call-decompressor`:
```rust
let runtime_call = <T as frame_system::Config>::RuntimeCall::decode_all_with_depth_limit(
    MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
    &mut &*substrate_data.runtime_call,
)
.map_err(HftError::RuntimeCallDecodeError)?;
```
and add a regression test analogous to `decompress_stack_exhaustion_poc` for `on_accept`.

### Proof of Concept
1. Build `RuntimeCall::Sudo(pallet_sudo::Call::sudo { call: Box::new(inner) })` nested ~1000 times (as in `modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs:313-352`), SCALE-encode it.
2. Wrap it as `SubstrateCalldata { signature: None, runtime_call: <encoded bytes> }`, SCALE-encode.
3. ABI-encode a `Message` whose `data` field is that byte string, with a valid `to`/`amount`/`from` for an existing `ContractToAsset` mapping.
4. Deliver as the `body` of an ISMP `PostRequest` to the `hyper-fungible-token` module's `on_accept` via the normal relayer/dispatch path.
5. `T::RuntimeCall::decode` at `module.rs:189` recurses through the nested `Sudo` calls without a depth bound and overflows the stack, crashing the node.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-122)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-200)
```rust
			let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
				.map_err(HftError::RuntimeCallDecodeError)?;
			// Apply the runtime's base call filter so that cross-chain calls cannot
			// reach dispatchables that the runtime has otherwise filtered out (e.g.
			// during a maintenance mode or a SafeMode period).
			if !<T as frame_system::Config>::BaseCallFilter::contains(&runtime_call) {
				Err(HftError::CallFiltered)?
			}
			use sp_runtime::traits::Dispatchable;
			runtime_call
				.dispatch(RawOrigin::Signed(origin.clone()).into())
				.map_err(|e| HftError::CallDispatchError(e.error))?;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L146-153)
```rust
			let decompressed = Self::decompress(compressed.clone(), encoded_call_size.clone())
				.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;

			let runtime_call = T::RuntimeCall::decode_all_with_depth_limit(
				MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
				&mut &decompressed[..],
			)
			.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;
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
