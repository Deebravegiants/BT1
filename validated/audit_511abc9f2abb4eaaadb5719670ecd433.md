Confirmed: both the `nexus` and `gargantua` runtimes include `pallet_hyper_fungible_token` alongside `pallet_sudo` and `pallet_utility`, which produce a recursive `RuntimeCall` enum (`Sudo(sudo { call: Box<RuntimeCall> })`, `Utility(batch { calls: Vec<RuntimeCall> })`). This confirms the analog is reachable and exploitable in the actual production runtime configuration. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Unbounded-depth SCALE decode of attacker-controlled cross-chain calldata causes stack overflow in HyperFungibleToken's `on_accept` - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
The `pallet_hyper_fungible_token` ISMP module decodes an attacker-controlled `runtime_call` byte blob using plain `Decode::decode`, with no recursion-depth limit, unlike the sibling `pallet_call_decompressor` pallet, which explicitly guards the same class of input using `decode_all_with_depth_limit` with a documented `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT`.

### Finding Description
`Pallet::<T>::on_accept` is the `IsmpModule` handler invoked whenever an ISMP `PostRequest` destined for the token module is delivered by a relayer via `pallet_ismp`'s message-handling entrypoints. The request `body` is ABI-decoded into a `Message`, and if `message.data` is non-empty, it is SCALE-decoded into `SubstrateCalldata`, whose `runtime_call` field is arbitrary attacker-supplied bytes originating from the source-chain contract: [4](#0-3) 

That `runtime_call` is then decoded directly into the runtime's aggregated `RuntimeCall` enum with no depth limit: [5](#0-4) 

Both the `nexus` and `gargantua` runtimes compose `RuntimeCall` from pallets that are recursive by construction — `pallet_sudo::Call::sudo { call: Box<RuntimeCall> }` and `pallet_utility::Call::{batch, batch_all, force_batch}(calls: Vec<RuntimeCall>)` — and both runtimes include `pallet_hyper_fungible_token` in the same `RuntimeCall`: [3](#0-2) [2](#0-1) 

The codebase already recognizes this exact bug class: `pallet_call_decompressor` was hardened against it, with an explicit comment and regression test (`decompress_stack_exhaustion_poc`) confirming that plain SCALE decoding of deeply nested `Sudo(Sudo(Sudo(...)))` calls causes decode-time stack exhaustion unless bounded by `decode_all_with_depth_limit`: [6](#0-5) [7](#0-6) 

The `hyper-fungible-token` module's `on_accept` path never applies this mitigation, using unguarded `T::RuntimeCall::decode` instead of `decode_all_with_depth_limit`.

### Impact Explanation
The `on_accept` entrypoint is reachable by any relayer delivering a valid cross-chain `PostRequest` from a registered source contract (`ContractToAsset` lookup only checks that a contract is *mapped*, not that the caller of that contract's transfer function is privileged). If the mapped ERC20-bridge contract allows any user to include arbitrary `data` in a bridged transfer (as is standard for these bridge contracts), an unprivileged sender can embed a deeply nested `RuntimeCall` encoding in `SubstrateCalldata.runtime_call`. Decoding this deeply nested value with the plain `Decode` trait recurses once per nesting level with no bound, exhausting the collator/validator's call stack and crashing (or otherwise faulting) the node processing the block — a permanent denial of service against message delivery for the state machine, since the same crash recurs on retry/block re-execution.

### Likelihood Explanation
This requires the target runtime to include recursive-call pallets (`pallet_sudo` and/or `pallet_utility`) in the same `RuntimeCall` as `pallet_hyper_fungible_token`, which is exactly the current production configuration in both `gargantua` and `nexus` runtimes. No signature or privileged origin is needed to reach `on_accept`; only a bridged token transfer with malicious calldata via any contract already registered for bridging.

### Recommendation
Replace the unguarded `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` call in `modules/pallets/hyper-fungible-token/src/module.rs` with `T::RuntimeCall::decode_all_with_depth_limit(MAX_DEPTH, &mut &*substrate_data.runtime_call)`, using the same bounded-depth approach already established in `pallet_call_decompressor`, and add a regression test analogous to `decompress_stack_exhaustion_poc` for the token module's calldata path.

### Proof of Concept
1. Construct a deeply nested `RuntimeCall` value, e.g. `Sudo(sudo { call: Box::new(Sudo(sudo { call: Box::new(...) })) })` repeated ~1000+ times (as done in the existing `decompress_stack_exhaustion_poc` test), or an equivalent `Utility::batch` nesting.
2. SCALE-encode it and place the bytes into `SubstrateCalldata.runtime_call` (with `signature: None`), then SCALE-encode `SubstrateCalldata` into `Message.data`.
3. ABI-encode the resulting `Message` (with a valid registered `from`/`source` contract mapping and a minimal transfer amount) as the ISMP `PostRequest` body.
4. Have a relayer submit this request through `pallet_ismp`'s handling entrypoint so `HyperFungibleToken::on_accept` executes.
5. Observe that `T::RuntimeCall::decode` at `modules/pallets/hyper-fungible-token/src/module.rs:189` recurses unboundedly and exhausts the stack, analogous to the confirmed stack-exhaustion behavior demonstrated for `pallet_call_decompressor` in `pallet_call_decompressor.rs:313-351` (the only difference being that pallet already has a depth-limit guard that this path lacks).

### Citations

**File:** parachain/runtimes/nexus/src/lib.rs (L1159-1161)
```rust
	pub type BeefyConsensusProofs = pallet_beefy_consensus_proofs;
	#[runtime::pallet_index(98)]
	pub type HyperFungibleToken = pallet_hyper_fungible_token;
```

**File:** parachain/runtimes/gargantua/src/lib.rs (L601-605)
```rust
impl pallet_sudo::Config for Runtime {
	type RuntimeEvent = RuntimeEvent;
	type RuntimeCall = RuntimeCall;
	type WeightInfo = weights::pallet_sudo::WeightInfo<Runtime>;
}
```

**File:** parachain/runtimes/gargantua/src/lib.rs (L948-950)
```rust
	pub type Sudo = pallet_sudo;
	#[runtime::pallet_index(26)]
	pub type CollatorManager = pallet_collator_manager;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-122)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-190)
```rust
			let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
				.map_err(HftError::RuntimeCallDecodeError)?;
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

**File:** modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs (L313-351)
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
```
