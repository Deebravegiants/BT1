### Title
Uncontrolled recursion (stack exhaustion) when decoding nested `RuntimeCall`s via ordinary signed/unsigned extrinsics is unguarded outside `pallet-call-decompressor` - ([File: modules/pallets/call-decompressor/src/lib.rs])

### Summary
`pallet-call-decompressor` was hardened against unbounded recursion during `RuntimeCall` decoding by switching from plain `Decode::decode` to `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT = 4, ...)`, with an explicit regression test (`decompress_stack_exhaustion_poc`) proving that a `RuntimeCall` nested ~1000 levels deep (`Sudo(Sudo(Sudo(...)))`) must be rejected. That same nested-`RuntimeCall` decoding path is reachable through every other route into the runtime — ordinary signed extrinsic submission and `Executive::validate_transaction` — which decode `UncheckedExtrinsic<Address, RuntimeCall, Signature, SignedExtra>` with plain `Decode::decode`, not the bounded-depth variant. This is the same bug class as GHSA-hv87-47h9-jcvq/CVE-2018-20993: an attacker-controlled, deeply nested input structure is deserialized with no application-level recursion bound, risking stack exhaustion/abort.

### Finding Description
`pallet_call_decompressor::Pallet::decode_and_execute` and its `validate_unsigned` path explicitly bound `RuntimeCall` decoding depth: [1](#0-0) [2](#0-1) [3](#0-2) 

The regression test that motivated this fix nests `pallet_sudo::Call::sudo { call: Box<RuntimeCall> }` ~1000 times and confirms it is rejected only because of the explicit depth limit: [4](#0-3) 

However, every runtime (`gargantua`, `nexus`) defines its normal `UncheckedExtrinsic` as `generic::UncheckedExtrinsic<Address, RuntimeCall, Signature, SignedExtra>`, which is decoded via plain `codec::Decode` (not `decode_all_with_depth_limit`) inside `Executive::validate_transaction`/block execution: [5](#0-4) [6](#0-5) 

`RuntimeCall` is a recursive enum (via `pallet_sudo::Call::sudo(Box<RuntimeCall>)`, `pallet_utility` batch calls, `pallet_proxy::proxy`, etc.), so an attacker can craft a signed extrinsic whose `function: RuntimeCall` field nests these recursive variants arbitrarily deep and submit it as an ordinary transaction. This path relies solely on whatever generic recursion guard `parity-scale-codec`'s default `Decode::decode` provides — the pallet's own author judged that guard insufficient for this runtime's actual stack budget, which is exactly why they capped `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT` at 4 rather than trusting the library default.

### Impact Explanation
A deeply nested `RuntimeCall` submitted as a normal signed extrinsic is decoded during `validate_transaction` (mempool gossip/tx-pool validation on every node) and again during block execution, before any weight/fee/origin checks run. If the codec's built-in default nesting bound is not tight enough for the actual constrained call stack of the runtime's WASM execution environment — as the pallet-call-decompressor fix and its dedicated PoC test imply — decoding such an extrinsic can exhaust the stack and abort/crash the validating node. Because this affects `validate_transaction` on every full node/collator that receives the transaction via gossip, this is a network-wide availability (DoS) impact, matching CWE-674 / the reported advisory's `C:N/I:N/A:H` profile.

### Likelihood Explanation
Any unprivileged account holder can construct and submit such an extrinsic since decode happens before signature/origin verification gates the specific call variant; only a funded signer or valid unsigned-extrinsic slot is required to get the bytes into the mempool/block. `pallet_sudo`, `pallet_utility`, and `pallet_proxy` calls that wrap `Box<RuntimeCall>` are present in the production runtimes, giving the attacker the recursive primitive needed.

### Recommendation
Apply the same bounded-depth decode used in `pallet_call_decompressor::decode_and_execute` to the primary extrinsic decode path: decode `RuntimeCall`/`UncheckedExtrinsic` with `decode_all_with_depth_limit` (or an equivalent low, audited bound) inside `Executive`/`validate_transaction`, or lower/verify `parity-scale-codec`'s global default nesting-depth constant to a value proven safe for this runtime's WASM stack, consistent with the `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT = 4` already established as safe for the same `RuntimeCall` type.

### Proof of Concept
Adapt the existing PoC (`modules/pallets/testsuite/src/tests/pallet_call_decompressor.rs:313-352`) to the normal extrinsic path instead of the decompressor: build `nested_calls` by wrapping `frame_system::Call::remark` in `pallet_sudo::Call::sudo { call: Box::new(...) }` ~1000 times, `encode()` it as `RuntimeCall`, wrap it in a `generic::UncheckedExtrinsic` (signed with any funded test account), and submit it through `Executive::validate_transaction`/`apply_extrinsic` directly (bypassing `pallet_call_decompressor` entirely) to show the plain `Decode::decode` path is not protected by `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT`.

### Citations

**File:** modules/pallets/call-decompressor/src/lib.rs (L46-51)
```rust
const ONE_MB: u32 = 1_000_000;
/// This is the maximum nesting level required to decode
/// the supported ismp messages and pallet_ismp_relayer calls
/// All suported call types require a recursion depth of 2 except calls containing Ismp Get requests
/// Ismp Get requests have a nested vector of keys requiring an extra recursion depth
const MAX_EXTRINSIC_DECODE_DEPTH_LIMIT: u32 = 4;
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

**File:** parachain/runtimes/gargantua/src/lib.rs (L167-169)
```rust
/// Unchecked extrinsic type as expected by this runtime.
pub type UncheckedExtrinsic =
	generic::UncheckedExtrinsic<Address, RuntimeCall, Signature, SignedExtra>;
```

**File:** parachain/runtimes/gargantua/src/lib.rs (L1128-1136)
```rust
	impl sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block> for Runtime {
		fn validate_transaction(
			source: TransactionSource,
			tx: <Block as BlockT>::Extrinsic,
			block_hash: <Block as BlockT>::Hash,
		) -> TransactionValidity {
			Executive::validate_transaction(source, tx, block_hash)
		}
	}
```
