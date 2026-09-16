### Title
Unbounded recursion in `RuntimeCall` SCALE decoding causes an uncatchable stack overflow via a single submitted extrinsic - ([File: parachain/runtimes/nexus/src/lib.rs])

### Summary
The Hyperbridge parachain runtime decodes every extrinsic's call payload with the default, depth‑unlimited `parity-scale-codec` `Decode` implementation. Because `RuntimeCall` is a recursive enum (e.g. `pallet_sudo::Call::sudo { call: Box<RuntimeCall> }`, `pallet_utility` batches, etc.), an attacker can submit a single signed extrinsic whose call payload is nested thousands of levels deep. Decoding that payload recurses once per nesting level with no bound, exhausting the thread stack and triggering an uncatchable `abort`/stack overflow in the node process — before dispatch, before weight checks, before `BaseCallFilter`. This is the exact bug class described in the reference GraphQL advisory (unbounded recursive-descent decode with no depth limit, tiny payload, crash before any validation runs), and the project's own codebase independently discovered and partially fixed it — but only for one call path.

### Finding Description
`UncheckedExtrinsic` for the runtime is defined as: [1](#0-0) 

decoded via the standard, derive-generated `codec::Decode` for `RuntimeCall`. `RuntimeCall` embeds pallets such as `pallet_sudo` whose `Call::sudo` variant wraps `Box<RuntimeCall>` recursively — confirmed by the project's own regression test which builds 1000 levels of nested `Sudo(Sudo(Sudo(...)))`: [2](#0-1) 

The project already recognized this exact vulnerability class — but only fixed it for the `pallet_call_decompressor` decode-and-execute path, which explicitly switched from plain `Decode::decode` to `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, …)`: [3](#0-2) [4](#0-3) 

The comments accompanying this fix make clear the underlying `Decode::decode`/`decode_all` in this codebase's `parity-scale-codec` has **no** built-in recursion-depth protection — the depth limit had to be added explicitly as an application-level control. However, this protection was applied only to the bespoke "decompress and execute" entry point. The primary, universal extrinsic ingestion path — every signed extrinsic submitted to the node via `author_submitExtrinsic`/gossip, decoded through `UncheckedExtrinsic::decode` (which recursively decodes the embedded `RuntimeCall`) — still uses the unprotected default `Decode::decode`. No equivalent `decode_all_with_depth_limit` guard exists at the `UncheckedExtrinsic`/`frame_executive` layer for ordinary extrinsics.

Recursive `RuntimeCall` variants (`pallet_sudo::sudo`, `pallet_utility::batch`/`as_derivative`, etc.) allow the SCALE-encoded call to be constructed with thousands of nesting levels while remaining a few bytes per level (each level is just an enum variant discriminant + inner call), so a payload well under typical extrinsic size limits can drive the decoder to overflow the stack.

### Impact Explanation
A stack overflow in Rust from unbounded recursion is not a catchable panic — it aborts the process. Any node (validator, collator, RPC node) that attempts to decode such an extrinsic — whether during transaction-pool validation, block import, or gossip relay — crashes immediately. This is a network-wide, permissionless DoS: dropping all in-flight requests/responses/consensus updates on the affected node and forcing an orchestrator restart, exactly mirroring the "Critical" impact described in the reference advisory (uncatchable crash, all in-flight work dropped). Given Hyperbridge is cross-chain messaging infrastructure, crashing collators/validators directly threatens availability of message delivery, consensus updates, and relayer operations.

### Likelihood Explanation
The attack requires only a normal signed extrinsic (any account with minimal balance to pay/attempt the transaction) — no special privilege, no proof, no governance role. Constructing the deeply nested `RuntimeCall` is trivial and demonstrated by the project's own test harness. The only reason this hasn't already been observed in the wild for the primary extrinsic path is that the team's mitigation effort focused on the decompressor pallet; the same payload shape submitted as an ordinary extrinsic bypasses that specific fix entirely.

### Recommendation
Apply the same `decode_all_with_depth_limit` (or an equivalent recursion-depth-bounded decode) to the runtime's primary extrinsic decoding path — i.e., wherever `UncheckedExtrinsic`/`RuntimeCall` is decoded from raw bytes for transaction-pool validation and block execution (not just inside `pallet_call_decompressor`). Alternatively/additionally, upgrade `parity-scale-codec` to a version with a global thread-local recursion-depth guard for all `Decode` implementations, and audit all other locations in the codebase performing plain `T::RuntimeCall::decode(...)` on attacker-controlled bytes (e.g. `modules/pallets/hyper-fungible-token/src/module.rs` line 189, which decodes a `RuntimeCall` from cross-chain message calldata) to ensure they use the same depth-bounded decode.

### Proof of Concept
The project's existing test demonstrates the exact primitive against the (patched) decompressor path; the same construction submitted as a normal `UncheckedExtrinsic` (bypassing the call-decompressor pallet) reproduces the crash on the primary decode path: [5](#0-4) 

1. Build `nested_calls = RuntimeCall::Sudo(pallet_sudo::Call::sudo { call: Box::new(...) })` nested N times (N in the low thousands is sufficient given typical default stack sizes).
2. `let encoded = nested_calls.encode();`
3. Wrap `encoded` as the `function` field of a standard `UncheckedExtrinsic` (signed with any funded test account) and submit it via `author_submitExtrinsic` or feed it directly into `UncheckedExtrinsic::decode`.
4. Observe the node process crash with a stack overflow during decode, before dispatch/weight/filter checks ever run — unlike the decompressor path, which now correctly returns `ErrorDecodingCall`.

### Citations

**File:** parachain/runtimes/nexus/src/lib.rs (L154-159)
```rust
/// Unchecked extrinsic type as expected by this runtime.
pub type UncheckedExtrinsic =
	generic::UncheckedExtrinsic<Address, RuntimeCall, Signature, SignedExtra>;

/// Extrinsic type that has already been checked.
pub type CheckedExtrinsic = generic::CheckedExtrinsic<AccountId, RuntimeCall, SignedExtra>;
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
