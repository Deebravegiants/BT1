### Title
Unbounded-depth SCALE decoding of an attacker-supplied `RuntimeCall` from cross-chain message calldata enables node crash via stack-overflow deserialization - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler decodes an attacker-controlled `Vec<u8>` (`substrate_data.runtime_call`, taken from the bridged `Message.data` field) directly into `T::RuntimeCall` using the plain `Decode::decode`, with no recursion-depth limit, before dispatching it. This is the same bug class as the BlazeDS advisory: untrusted bytes are fed straight into a generic deserializer for a type whose decoder recurses through its own variants, and no bound is placed on that recursion.

### Finding Description
In `modules/ismp/pallets/hyper-fungible-token/src/module.rs`, `on_accept` (invoked whenever a POST request lands on this module through the ordinary `handle_unsigned` → `execute` → router → `IsmpModule::on_accept` path — reachable by any relayer submitting a valid proof for a message originating from the registered HFT bridge contract) does: [1](#0-0) 

then [2](#0-1) 

`substrate_data.runtime_call` is a raw `Vec<u8>` field of `SubstrateCalldata` (`modules/pallets/hyper-fungible-token/src/types.rs`), and its bytes originate from the `data` field of the ABI-encoded `Message` struct that any caller of `HyperFungibleToken.sol` / `WrappedHyperFungibleToken.sol` `send()` supplies on the source chain — i.e. it is fully attacker-controlled content that only needs to pass ISMP proof verification for message delivery, not any content restriction.

`T::RuntimeCall` is the aggregated runtime `Call` enum, which is recursive: dispatchables like `Utility::batch`, `Utility::as_derivative`, `Proxy::proxy`, `Scheduler::schedule`, etc. embed `Box<RuntimeCall>` / `Vec<RuntimeCall>` inside themselves. `codec::Decode`'s derived implementation for such recursive enums recurses on the Rust call stack once per nesting level with no depth limit, so a maliciously crafted, deeply-nested SCALE-encoded call (e.g. thousands of nested `Utility::batch` wrappers) can drive the decoder into a stack overflow, which in Rust aborts the process rather than returning an `Err`.

Crucially, the codebase is aware of exactly this hazard and has already fixed it elsewhere: `modules/pallets/call-decompressor/src/lib.rs` decodes the very same `T::RuntimeCall` type using `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)`: [3](#0-2) 

`module.rs`'s `on_accept` uses the unguarded `Decode::decode` on the same recursive `RuntimeCall` type, sourced from data that is strictly less trusted than an ordinary unsigned extrinsic (it arrives from a foreign, non-substrate chain via a bridge contract call parameter).

### Impact Explanation
A stack-overflow abort inside `on_accept`, which executes inside `pallet_ismp::Pallet::execute` during `handle_unsigned` (an unsigned, free-to-submit extrinsic validated and then dispatched by every full node/collator that processes the block), crashes the node process handling that block — not merely reverts the extrinsic. Because `handle_unsigned` messages are processed by every collator/validator that must import/execute the block, a single malicious message can be crafted once, relayed, and processed identically by every node in the network, producing a synchronized crash across the network (a chain halt), which directly satisfies "a route unable to deliver messages" — all subsequent ISMP messages (including the token bridge itself) stop being processed until the runtime is patched. This is Medium/High severity: it is a network-wide DoS on the messaging pallet caused by unsafe deserialization of untrusted, attacker-supplied bytes, mirroring the BlazeDS CWE-502 bug class (unrestricted deserialization of untrusted data with harmful side effects), though here the side effect is stack-exhaustion/crash rather than arbitrary code execution.

### Likelihood Explanation
Reachable from a single, permissionless relayed message: any account can call `send()` on the registered `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM contract with an arbitrary `data` payload, have a relayer deliver the resulting POST request with a valid state proof, and have the on-chain module decode+dispatch the embedded `RuntimeCall`. No admin/governance action or special privilege is needed — only that the message's `source`/`from` correspond to a `ContractToAsset`-registered bridge contract, which is a normal, expected bridging configuration, not a barrier to an ordinary end user of the bridge. The `BaseCallFilter` check happens only *after* the vulnerable decode, so it provides no protection against the crash. I could not fully verify (due to index limits) whether `decode()`'s stack-overflow failure mode is caught anywhere upstream (e.g., a `catch_unwind` wrapper around message execution in the collator's block-import path); no such wrapper was found in `modules/pallets/ismp/src/impls.rs` or the runtime's message-queue/executive code within the accessible index, which is consistent with there being no mitigation, but this could not be conclusively ruled out everywhere in the workspace.

### Recommendation
Replace `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` (and, defensively, `SubstrateCalldata::decode`) in `modules/pallets/hyper-fungible-token/src/module.rs` with a depth-limited decode, mirroring `call-decompressor`'s pattern:
```rust
let runtime_call = T::RuntimeCall::decode_all_with_depth_limit(
    MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
    &mut &*substrate_data.runtime_call,
).map_err(HftError::RuntimeCallDecodeError)?;
```
Apply the same depth-limited decode consistently to every place across the codebase that decodes an untrusted byte blob into a recursive `RuntimeCall` (or any other self-referential/recursive SCALE type) sourced from cross-chain message bodies, not just from local extrinsics.

### Proof of Concept
1. Attacker calls `send()` on the registered `HyperFungibleToken` EVM contract (or equivalent), setting `Message.data` to a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <deeply nested Utility::batch(...) blob> }`, nested to a depth sufficient to exceed the thread stack (e.g. tens of thousands of levels, each only a few bytes of SCALE overhead — cheap to construct within reasonable calldata/body size limits).
2. A relayer observes the POST request and its proof of finality/inclusion and submits it via `Ismp::handle_unsigned` (free, unsigned, and available to any relayer/node).
3. Router dispatches to `HyperFungibleToken::on_accept`, which reaches `SubstrateCalldata::decode` then `T::RuntimeCall::decode`, recursing once per nesting level of the crafted call with no depth cap.
4. Recursion exhausts the executing thread's stack; the process aborts on stack overflow. Every node executing/importing the block hits the same crash deterministically, since block execution is deterministic — resulting in a chain-wide halt of ISMP message processing.

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
