### Title
Unbounded-depth `Decode` of Untrusted Cross-Chain Calldata into `RuntimeCall` Enables Dispatch-Time Stack Overflow / Halted Message Route - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`HftModule::on_accept` decodes the `data` field of an incoming cross-chain token transfer directly into `T::RuntimeCall` using plain `codec::Decode::decode`, with no recursion-depth bound, before dispatching it. `T::RuntimeCall` is a deeply recursive SCALE type (it nests calls such as `Utility::batch`/`batch_all` which themselves contain `Vec<RuntimeCall>`), and `parity-scale-codec`'s default `Decode` has no depth limiting — an attacker-controlled, deeply-nested encoding can exhaust the stack during decode. This is the exact bug class the same codebase already fixed elsewhere (`pallet-call-decompressor`) by switching to `decode_all_with_depth_limit`, but the fix was not applied here.

### Finding Description
In `on_accept`, once a cross-chain post request from a registered bridge contract is decoded, any nonempty `message.data` is treated as `SubstrateCalldata` and its `runtime_call` bytes are handed straight to the generic dispatch machinery: [1](#0-0) [2](#0-1) 

`T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` uses the plain, unbounded `Decode` implementation. There is no equivalent to the depth-limited decode used elsewhere in this repository for the identical situation — decoding an untrusted, attacker-supplied byte blob into the runtime's own dispatchable `Call` enum before executing it: [3](#0-2) [4](#0-3) 

`pallet-call-decompressor` explicitly guards this same operation with `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)` precisely because a raw `RuntimeCall::decode` on untrusted bytes is unsafe. `pallet-hyper-fungible-token` performs the structurally identical operation — decoding untrusted, attacker-chosen bytes into `T::RuntimeCall` prior to dispatch — but omits the depth limit.

`message.data` originates from the ISMP `PostRequest.body`, which is ABI-decoded from data supplied by the source-chain sender through the registered bridge contract (`ContractToAsset` only authenticates which contract/asset pair is trusted, not the content of arbitrary calldata a user asks that contract to relay). Reaching this code therefore only requires: (1) a legitimate, already-registered token bridge contract on the source chain, and (2) any user of that bridge choosing to attach calldata — i.e., it is reachable by an ordinary, unprivileged bridge user/relayer, matching the required threat model (message dispatcher/relayer/token bridger).

### Impact Explanation
`handle_unsigned` executes ISMP messages, including calls into `IsmpModule::on_accept`, as part of normal (unsigned, fee-free) block execution. A crafted, deeply-nested `RuntimeCall` encoding inside `substrate_data.runtime_call` can drive the decoder into unbounded recursion, causing a stack overflow during decode. In a Substrate/WASM execution context this is a hard abort of block execution rather than a graceful `DispatchError`, which can prevent the node from processing the batch (and, depending on WASM stack behavior, potentially the block) at all — i.e., a route that becomes unable to deliver messages, since any subsequent relaying of the same or similarly crafted payload keeps failing the same way for every node that attempts to execute it. This falls under the accepted impact category "a route unable to deliver messages."

### Likelihood Explanation
Likelihood is high for any hyper-fungible-token deployment: constructing a deeply nested `RuntimeCall` (e.g., nested `Utility::batch` calls) is straightforward and requires no special privilege — only a bridge contract already registered in `ContractToAsset`, which is the module's intended, expected configuration for legitimate use. No signature or special origin is needed to reach the vulnerable decode, since it happens unconditionally whenever `message.data` is nonempty, before the (optional) signature branch is even evaluated.

### Recommendation
Replace `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` in `on_accept` with a depth-limited decode, mirroring the pattern already used in `pallet-call-decompressor` (`decode_all_with_depth_limit` with a bounded `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT`), and reject calldata whose encoding exceeds that limit with a typed error instead of allowing the decoder to recurse unbounded.

### Proof of Concept
1. Construct a `RuntimeCall::Utility(Call::batch { calls: vec![...] })` where each element is itself a nested `Utility::batch` call, recursed to a depth sufficient to exceed the thread/WASM execution stack (well within the size limits otherwise imposed on `message.data`/proof payloads).
2. SCALE-encode this into `SubstrateCalldata.runtime_call` with `signature: None`.
3. ABI-encode a `Message` whose `data` field is this `SubstrateCalldata`, and dispatch it as `PostRequest.body` from a contract already registered in `ContractToAsset`.
4. Relay this request via `pallet_ismp::Call::handle_unsigned`; when `HftModule::on_accept` reaches `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)`, the unbounded recursive decode overflows the stack instead of returning `HftError::RuntimeCallDecodeError`.

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

**File:** modules/pallets/call-decompressor/src/lib.rs (L149-153)
```rust
			let runtime_call = T::RuntimeCall::decode_all_with_depth_limit(
				MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
				&mut &decompressed[..],
			)
			.map_err(|_| TransactionValidityError::Invalid(InvalidTransaction::Call))?;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L264-268)
```rust
		let runtime_call = <T as frame_system::Config>::RuntimeCall::decode_all_with_depth_limit(
			MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
			&mut &call_bytes[..],
		)
		.map_err(|_| Error::<T>::ErrorDecodingCall)?;
```
