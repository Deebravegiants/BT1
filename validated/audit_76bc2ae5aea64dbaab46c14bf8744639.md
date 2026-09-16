### Title
Unbounded-depth SCALE decode of an untrusted `RuntimeCall` in `hyper-fungible-token::on_accept` can crash message execution for every node - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` in the `hyper-fungible-token` pallet decodes an attacker-supplied byte blob directly into the runtime's `RuntimeCall` enum using plain `Decode::decode`, with no recursion/depth limit, before dispatching it. This is reachable end-to-end from an unprivileged token sender on the source chain via the bridge's `send()` call-data field, and is delivered to the destination chain as an ordinary ISMP `PostRequest` with a valid state proof — no elevated privilege is required.

### Finding Description
In `on_accept`: [1](#0-0) 
`message.data` — which is fully attacker-controlled `call_data` supplied by whoever calls `send()` on the source EVM contract — is decoded into `SubstrateCalldata`, whose `runtime_call: Vec<u8>` field is opaque attacker bytes.

That field is then decoded straight into the runtime's `RuntimeCall` enum: [2](#0-1) 
`T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` uses the plain, unbounded `codec::Decode::decode`, not `decode_all_with_depth_limit`. `RuntimeCall` in this codebase composes pallets such as `pallet_utility`/`pallet_proxy` (present in `parachain/runtimes/nexus/src/lib.rs`, referenced 29 times) whose call variants recursively embed another `RuntimeCall` (e.g. `Utility::batch(Vec<RuntimeCall>)`, `Proxy::proxy(RuntimeCall)`). SCALE's derived `Decode` for such enums recurses once per nesting level with no built-in bound, so a payload with sufficiently deep nesting drives the decode call to stack overflow and abort the process.

This is the exact bug class the codebase elsewhere treats as sensitive and hardens explicitly: `pallet-call-decompressor` decodes an untrusted, attacker-supplied encoded `RuntimeCall` using `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)` specifically to bound decode recursion: [3](#0-2) [4](#0-3) 
The `hyper-fungible-token` pallet's `on_accept` path performs the analogous decode of an equally untrusted, externally-supplied `RuntimeCall` blob but omits that protection entirely.

Crucially, `on_accept` executes deterministically for *every message*, on *every node* (the destination chain state machine), as part of ordinary ISMP message processing (`handle_unsigned` → `execute` → module router → `on_accept`) — it is not behind any privileged origin. Reaching it requires only: (1) calling `send()` on the bridge's EVM contract with a crafted `call_data`/`data` payload, and (2) a relayer submitting the resulting cross-chain message with a valid state proof, exactly the "unprivileged token bridger" + "relayer" combination in scope.

### Impact Explanation
A stack-overflow abort during `on_accept` occurs inside the deterministic message-execution path invoked by `pallet_ismp::handle_unsigned`/`execute`. Because this runs identically on every full node applying the block, a single malicious cross-chain token transfer with a deeply-nested encoded `RuntimeCall` in its optional calldata can crash block execution across the network, halting further ISMP message delivery for the affected chain — i.e., "a route unable to deliver messages," one of the accepted impact categories.

### Likelihood Explanation
Likelihood is high for any attacker willing to pay for a small ERC20-style transfer plus relaying fees: crafting a deeply nested `Utility::batch`/`Proxy::proxy` SCALE payload of a few hundred bytes is trivial, and the calldata path is only exercised when `message.data` is non-empty — fully attacker-selected. No signature or special permission gates the vulnerable decode call itself (the decode happens before/independent of the later signature check on `substrate_data.signature`).

### Recommendation
Bound the recursion depth when decoding the untrusted `runtime_call` bytes, mirroring the existing safeguard in `pallet-call-decompressor`:
```rust
let runtime_call = <T as frame_system::Config>::RuntimeCall::decode_all_with_depth_limit(
    MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
    &mut &*substrate_data.runtime_call,
)
.map_err(HftError::RuntimeCallDecodeError)?;
```
Also consider capping `substrate_data.runtime_call.len()` before decode to reject obviously oversized/malicious payloads early, consistent with the size-bound pattern used in `pallet_call_decompressor::decompress`.

### Proof of Concept
1. On the source EVM chain, call the bridge contract's `send()` with a `to` value the attacker controls and `call_data` set to the SCALE encoding of `SubstrateCalldata { signature: None, runtime_call: <encoded_call> }`, where `<encoded_call>` is a deeply self-nested `RuntimeCall::Utility(pallet_utility::Call::batch { calls: vec![RuntimeCall::Utility(pallet_utility::Call::batch { calls: vec![ ... ] })] })` nested to a depth sufficient to exceed the thread's stack (a few thousand levels, well within a reasonably sized extrinsic).
2. A relayer submits the resulting `PostRequest` with a valid consensus/state proof via `pallet_ismp::handle_unsigned`.
3. During execution, the destination chain routes the request to `hyper-fungible-token::on_accept`, which reaches `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` at `modules/pallets/hyper-fungible-token/src/module.rs:189` and overflows the stack, aborting the node process that is applying the block — reproducible deterministically on every validating node.

*Note: I was unable to directly verify the exact `RuntimeCall` variant wiring in the specific runtime that includes `hyper-fungible-token` (only `nexus`/`gargantua` runtime files were checked for `pallet_utility`/`pallet_proxy` presence), nor execute the decode to empirically confirm the stack-overflow threshold; this should be confirmed with a runtime-level fuzz/PoC before treating severity as final.*

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
