### Title
Unbounded-recursion-depth SCALE decode of attacker-supplied `RuntimeCall` in HFT cross-chain calldata leads to stack-overflow DoS - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`pallet-hyper-fungible-token`'s `IsmpModule::on_accept` decodes an attacker-controlled `runtime_call` byte blob with the plain, depth-unbounded `codec::Decode::decode`, instead of the depth-limited decode this codebase already uses elsewhere for exactly this class of attack.

### Finding Description
`on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs` handles an incoming cross-chain ISMP `PostRequest` for a bridged-token transfer. If `message.data` is non-empty, it SCALE-decodes it as `SubstrateCalldata` and then decodes the embedded field with: [1](#0-0) 

```rust
let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
    .map_err(HftError::RuntimeCallDecodeError)?;
```

`SubstrateCalldata::runtime_call` is a plain `Vec<u8>` field fully controlled by whoever emits the source-chain `Message` (any caller of the bridged `HyperFungibleToken`/`WrappedHyperFungibleToken` contract's transfer method — an ordinary token bridger, not a privileged party): [2](#0-1) 

The runtime's `RuntimeCall` enum contains recursively boxed variants (`pallet_sudo::Call::sudo { call: Box<RuntimeCall> }`, `pallet_utility`, `pallet_proxy`, etc.), so an attacker can SCALE-encode thousands of nested wrapper calls and place that blob in `data`. `T::RuntimeCall::decode` here uses the plain, unbounded-depth `Decode` trait method — no `decode_all_with_depth_limit` call, no explicit recursion cap.

This codebase has already identified and fixed exactly this bug class elsewhere: `pallet-call-decompressor` explicitly decodes `RuntimeCall` with a tight custom bound: [3](#0-2) [4](#0-3) 

and has a regression test proving that 1000 nested `Sudo(Sudo(...))` calls are what the fix guards against: [5](#0-4) 

The HFT module's `on_accept` path reaches the identical decode target (`T::RuntimeCall`) with an identical attacker-controlled nested-call payload shape, but without that mitigation.

### Impact Explanation
Any relayer delivering a valid ISMP proof for a token-transfer message from a registered source contract triggers `on_accept`. If the attached `data` decodes to a `SubstrateCalldata` whose `runtime_call` bytes encode a sufficiently deep chain of nested `RuntimeCall` variants, the recursive `Decode` implementation recurses once per nesting level. As demonstrated by the codebase's own `decompress_stack_exhaustion_poc` test, this depth of recursion is enough to exhaust the native call stack during block execution/transaction-pool validation, crashing the node process — a denial of service on the parachain that processes the message (halting message delivery/finality for that chain), exactly analogous to the SnakeYAML stack-overflow DoS class in the reference advisory.

### Likelihood Explanation
High: reaching `on_accept` only requires delivering one valid, otherwise-legitimate cross-chain token-transfer proof with a crafted `data` field — no admin/governance privilege, no protocol-specific knowledge beyond the public `SubstrateCalldata`/`RuntimeCall` SCALE layout, both of which are part of the public interface documented for the pallet.

### Recommendation
Decode `substrate_data.runtime_call` with a depth-bounded decoder, mirroring the fix already applied in `pallet-call-decompressor`:
```rust
let runtime_call = <T as frame_system::Config>::RuntimeCall::decode_all_with_depth_limit(
    MAX_CALLDATA_DECODE_DEPTH_LIMIT,
    &mut &*substrate_data.runtime_call,
).map_err(HftError::RuntimeCallDecodeError)?;
```
choosing `MAX_CALLDATA_DECODE_DEPTH_LIMIT` no larger than what legitimate destination-chain calldata actually requires (as was done for `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT` in `call-decompressor`).

### Proof of Concept
1. Register a source EVM contract/asset via the normal HFT flow so `ContractToAsset` resolves.
2. Build a `RuntimeCall` value nested ~1000 levels deep using boxed variants (e.g. `pallet_sudo::Call::sudo` wrapping itself, as in `decompress_stack_exhaustion_poc`), SCALE-encode it, and place the bytes in `SubstrateCalldata.runtime_call` (with `signature: None`).
3. SCALE-encode `SubstrateCalldata` and place it as the `data` field of the ABI-encoded HFT `Message`, emitted from the registered source contract as a normal transfer-with-calldata request.
4. Relay a valid ISMP proof for this `PostRequest` via `handle_unsigned`; when `pallet_ismp` dispatches it to `on_accept`, `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` recurses through all nested levels and overflows the stack, crashing the node — the same effect the `decompress_stack_exhaustion_poc` regression test in `modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs` was written to prevent for the other decode path.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-190)
```rust
			let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
				.map_err(HftError::RuntimeCallDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L105-113)
```rust
/// SCALE-encoded calldata for executing a runtime call on the destination substrate chain
#[derive(Debug, Clone, Encode, Decode, scale_info::TypeInfo, PartialEq, Eq)]
pub struct SubstrateCalldata {
	/// Optional SCALE-encoded [MultiSignature](sp_runtime::MultiSignature) of the beneficiary's
	/// account nonce and the encoded runtime call
	pub signature: Option<Vec<u8>>,
	/// SCALE-encoded runtime call to execute
	pub runtime_call: Vec<u8>,
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

**File:** modules/pallets/call-decompressor/src/lib.rs (L263-268)
```rust
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
