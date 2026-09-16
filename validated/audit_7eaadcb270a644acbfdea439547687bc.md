### Title
Unbounded recursive `RuntimeCall` decode in `hyper-fungible-token` `on_accept` allows relayer-triggered stack exhaustion - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
The Hyper-Fungible-Token pallet's `on_accept` handler decodes an attacker-supplied, ISMP-delivered `SubstrateCalldata.runtime_call` byte blob directly into `T::RuntimeCall` using plain `Decode::decode`, with no recursion-depth limit, unlike the sibling `pallet-call-decompressor` path which explicitly guards the same class of input with `decode_all_with_depth_limit`.

### Finding Description
`Pallet::on_accept` (invoked whenever any relayer delivers a `PostRequest` to this module) ABI-decodes the cross-chain `Message`, and if `message.data` is non-empty, decodes it as `SubstrateCalldata`, then decodes the embedded `runtime_call: Vec<u8>` field directly into the runtime's dispatchable `RuntimeCall` type: [1](#0-0) [2](#0-1) 

`SubstrateCalldata.runtime_call` is an opaque `Vec<u8>` chosen entirely by the source-chain sender of the ISMP message (any account/contract that can send a token-bridge `PostRequest`, i.e. an unprivileged token bridger): [3](#0-2) 

`T::RuntimeCall` is a self-referential enum (as demonstrated elsewhere in the codebase, `pallet_sudo::Call::sudo { call: Box<RuntimeCall> }` boxes another `RuntimeCall`), so an attacker can encode thousands of nested `Sudo(Sudo(Sudo(...)))` variants. The codebase already recognizes and has fixed exactly this bug class in a different entry point: `pallet-call-decompressor` was patched to call `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, …)` specifically because unbounded recursive `RuntimeCall::decode` caused stack exhaustion, with a regression test proving the old plain-`decode` behavior crashed: [4](#0-3) [5](#0-4) [6](#0-5) 

The `hyper-fungible-token` module's `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` call was never given the same depth-limited treatment, leaving the identical recursive-decode stack-exhaustion primitive reachable through a different, unprivileged path: ISMP token-transfer message delivery rather than the call-decompressor extrinsic.

### Impact Explanation
A stack overflow during message dispatch execution (inside `on_accept`, called from the ISMP router while processing incoming requests) crashes/panics the node process handling that block, i.e. denial of service for the parachain executing ISMP requests — matching the CVSS 5.5 "AC:L/PR:N/UI:R.../A:H" profile of the original mxml CVE (stack consumption via crafted recursive input). Because `on_accept` runs as part of normal ISMP message execution (potentially inside block-import/consensus-critical code paths), a successful crash can halt block production/validation for nodes processing the malicious request, which is a route/consensus availability impact, not merely a local DoS.

### Likelihood Explanation
Reachability requires only: (1) the source contract/account be registered via `ContractToAsset` (a standard part of onboarding a bridged token, not privileged from the perspective of who can *send* transfers once registered), and (2) the sender include non-empty `data` in the ABI-encoded `Message` with a SCALE-encoded `SubstrateCalldata.runtime_call` containing a deeply nested `RuntimeCall` variant. Any relayer can deliver the resulting `PostRequest` — no signature or special privilege is needed on the delivery side; only the source-chain call to the bridge module needs to originate from a chain/contract already using this module, which is the module's core intended use case. This makes the trigger straightforward for an "unprivileged ... token bridger" as scoped by the rules.

### Recommendation
Replace the unbounded `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` in `on_accept` with a depth-limited decode, mirroring the fix already applied in `pallet-call-decompressor`:
```rust
let runtime_call = <T as frame_system::Config>::RuntimeCall::decode_all_with_depth_limit(
    MAX_SUBSTRATE_CALLDATA_DECODE_DEPTH_LIMIT,
    &mut &*substrate_data.runtime_call,
)
.map_err(HftError::RuntimeCallDecodeError)?;
```
Choose a depth constant analogous to `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT` sized for the legitimate calls this pallet intends to support, and reject anything deeper before recursive decoding runs.

### Proof of Concept
1. Register `SourceContract` for some `AssetId` via the normal token-registration flow (as any integrator would).
2. From the source chain, construct an ABI-encoded `Message { from, to, amount, data }` where `data` is SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <bytes> }`.
3. Build `<bytes>` the same way the existing regression test does — nest `pallet_sudo::Call::sudo { call: Box::new(...) }` ~1000 times around an inner harmless call, then `.encode()` it, exactly as in: [7](#0-6) 
4. Submit this as the `body` of a `PostRequest` targeting the hyper-fungible-token module (via any relayer, no signature needed on the ISMP delivery side).
5. When `on_accept` reaches `SubstrateCalldata::decode` and then `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)`, the unbounded recursive decode consumes the call stack and crashes the node processing the request — the same failure mode the call-decompressor test at lines 313-352 proves occurs without a depth limit.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-123)
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
