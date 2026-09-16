### Title
Unbounded-depth SCALE decode of attacker-controlled cross-chain calldata in `pallet-hyper-fungible-token::on_accept` enables stack-overflow DoS on message delivery - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
The vLLM advisory describes `pickle.loads()` deserializing attacker-supplied bytes into an arbitrary object without sanitization, on a reachable network path, causing unbounded computation/RCE. The closest reachable analog in this codebase is `pallet-hyper-fungible-token`'s `on_accept` handler, which SCALE-decodes an attacker-controlled byte blob directly into `T::RuntimeCall` — the full, recursively-nested runtime call enum — with no recursion-depth bound, unlike the sibling `pallet-call-decompressor`, which explicitly guards the same operation with `decode_all_with_depth_limit`.

### Finding Description
`IsmpModule::on_accept` for `pallet-hyper-fungible-token` decodes optional calldata carried inside every incoming cross-chain token-transfer message: [1](#0-0) 

then decodes the embedded `runtime_call` bytes with a plain, unbounded `Decode`: [2](#0-1) 

`T::RuntimeCall` is the full aggregated runtime call enum, which includes recursively-composable dispatchables such as `pallet_utility`'s batch calls and `pallet_proxy`'s wrapped-call dispatch (both configured in the `nexus`/`gargantua` runtimes). SCALE's derived `Decode` for such nested enums recurses once per nesting level with no depth tracking, so an attacker can encode a call whose nesting depth is bounded only by the message size limit, not by any explicit recursion guard.

This is the exact class of defect the codebase already recognizes and mitigates elsewhere: `pallet-call-decompressor::decode_and_execute` decodes an equally attacker-influenced `RuntimeCall` but does so via `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)`: [3](#0-2) 

with the constant explicitly documented as required for "all supported ismp messages and pallet_ismp_relayer calls": [4](#0-3) 

`pallet-hyper-fungible-token::on_accept`'s `T::RuntimeCall::decode` call has no equivalent bound, and unlike `call-decompressor` (which requires an unsigned extrinsic submission), this path is reached automatically by `pallet-ismp` whenever *any* relayer delivers a normal, permissionless cross-chain token transfer whose `Message.data` field is non-empty — the `on_accept` router callback runs unconditionally as part of ordinary message dispatch, before any of the later signature/origin checks are relevant to the decode step itself.

### Impact Explanation
A crafted, deeply nested `SubstrateCalldata.runtime_call` blob delivered as part of an otherwise ordinary token-transfer `PostRequest` will be decoded during `on_accept`, which executes inside block/extrinsic processing on every collator and full node validating the block. If the nesting depth is large enough to exhaust the Wasm execution stack, this becomes a state-transition-function fault reached by an unprivileged token bridge message rather than a benign decode error — the same malformed message must be reprocessed by every node attempting to import/finalize the block containing it, so the offending ISMP request can become a permanently undeliverable/poisoned message for the destination route (the delivery callback can never successfully return), which the validation criteria classifies as "a route unable to deliver messages." This is reachable by a single relayed message from an unprivileged sender (anyone who can call `send()` on the source-chain `HyperFungibleToken`/`WrappedHyperFungibleToken` contract with attacker-chosen calldata), requiring no governance or admin capability.

### Likelihood Explanation
Likelihood is high for triggering the fault: constructing a deeply nested `RuntimeCall` (e.g., recursively wrapped `Utility`/`Proxy` calls) and SCALE-encoding it requires no special access, no signature, and no elevated privilege — only a normal cross-chain send with a non-empty `data` field, which is a documented, user-facing feature of the token pallet. The only precondition is that the message actually reach `on_accept`, which happens for any successfully delivered request to the pallet's module id.

### Recommendation
Bound the recursion depth of the `runtime_call` decode in `on_accept`, mirroring the existing mitigation in `pallet-call-decompressor`: replace `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` with `T::RuntimeCall::decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, &mut &*substrate_data.runtime_call)` (or an equivalent shared constant), and apply the same bound to the outer `SubstrateCalldata::decode` if it can itself contain nested structures. Consider centralizing this depth-limited decode helper so any future pallet decoding an untrusted `RuntimeCall` from cross-chain calldata is forced to opt into the same protection.

### Proof of Concept
1. On the source chain, call `HyperFungibleToken.send(...)` (or the Substrate equivalent) with `data` set to `SubstrateCalldata { signature: None, runtime_call: <SCALE-encoded, deeply nested pallet_utility::Call::batch(vec![pallet_utility::Call::batch(vec![... repeated N times ...])])> }.encode()`.
2. Have a relayer deliver the resulting `PostRequest` to the destination chain's `pallet-hyper-fungible-token` module, as exercised by the existing test harness in `modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs::should_receive_asset_with_calldata` (same code path, replacing the simple `Balances::transfer_allow_death` call with the deeply nested call above).
3. `on_accept` reaches `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` at `modules/pallets/hyper-fungible-token/src/module.rs:189`, which recurses once per nesting level with no depth limit, exhausting the execution stack for sufficiently large N — compare against `pallet-call-decompressor`'s guarded `decode_all_with_depth_limit` call, which rejects the same shape of payload once nesting exceeds `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT`.

### Citations

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

**File:** modules/pallets/call-decompressor/src/lib.rs (L46-51)
```rust
const ONE_MB: u32 = 1_000_000;
/// This is the maximum nesting level required to decode
/// the supported ismp messages and pallet_ismp_relayer calls
/// All suported call types require a recursion depth of 2 except calls containing Ismp Get requests
/// Ismp Get requests have a nested vector of keys requiring an extra recursion depth
const MAX_EXTRINSIC_DECODE_DEPTH_LIMIT: u32 = 4;
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
