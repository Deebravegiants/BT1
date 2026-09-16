### Title
Unbounded-depth SCALE decode of attacker-controlled `RuntimeCall` in cross-chain calldata dispatch - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler decodes an attacker-supplied, SCALE-encoded `RuntimeCall` from the `data` field of an incoming cross-chain token message and dispatches it, using plain `Decode::decode` with no explicit recursion-depth bound [1](#0-0) . The codebase's own `pallet-call-decompressor`, which decodes and executes the same class of untrusted, attacker-supplied `RuntimeCall` bytes, was hardened against exactly this bug class by switching to `decode_all_with_depth_limit` with an explicit `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT`, with a dedicated regression test (`decompress_stack_exhaustion_poc`) proving that a deeply nested `RuntimeCall` (1000 nested `Sudo(sudo)` calls) is otherwise a live decode-time hazard [2](#0-1) [3](#0-2) . `pallet-hyper-fungible-token::on_accept` never applies this same mitigation to the equivalent attacker-controlled deserialization/dispatch path.

### Finding Description
When a `PostRequest` carrying a `HyperFungibleToken.Message` with non-empty `data` is accepted, `on_accept`:
1. ABI-decodes the message, mints/transfers tokens to the beneficiary, then
2. SCALE-decodes `message.data` into `SubstrateCalldata` [4](#0-3) ,
3. SCALE-decodes `substrate_data.runtime_call` (raw, attacker-supplied bytes from the source chain contract call) directly into `T::RuntimeCall` via plain `Decode::decode`, with no depth-limit API used [5](#0-4) ,
4. Runs it through `BaseCallFilter` and dispatches it as `RawOrigin::Signed(origin)` [6](#0-5) .

`substrate_data.runtime_call` is fully attacker-controlled: it comes from `message.data`, populated by whoever calls the source-chain `HyperFungibleToken`/`WrappedHyperFungibleToken` `send()` with calldata — an unprivileged bridge user, not a trusted party. In the unsigned branch, the dispatch `origin` is derived straight from `message.from` (the source-chain sender), so no signature check gates the decode step at all before the bytes reach `T::RuntimeCall::decode` [7](#0-6) .

This is the same "decode an attacker-supplied encoded `RuntimeCall`" primitive that `pallet-call-decompressor` deliberately hardened. That pallet's own doc explicitly frames the low, explicit depth bound as a defense against decode-time recursion blowups on this exact input shape [2](#0-1) , and both its `validate_unsigned` and `decode_and_execute` paths use `decode_all_with_depth_limit(MAX_EXTRINSIC_DECODE_DEPTH_LIMIT, ...)` rather than a bare `decode` [8](#0-7) [9](#0-8) . `pallet-hyper-fungible-token`'s functionally identical decode-and-dispatch step, reachable from an ordinary cross-chain token transfer rather than a privileged extrinsic, was not given the same treatment — it relies solely on whatever depth limit is implicit in the plain `Decode` derive, which the project's own regression test shows is not the layer they trust to stop this input shape (they added the explicit lower bound specifically because it was needed).

### Impact Explanation
`on_accept` runs during ISMP message delivery for every relayed cross-chain token transfer that carries calldata. A relayer or the attacker themselves can get a message with a maliciously deep/large `runtime_call` payload processed on the destination chain during ordinary message handling (the core dispatch/delivery path for the token bridge). If decode-time recursion exhausts the executor's stack, this crashes/panics block execution processing that message, which can render the channel unable to deliver messages and, depending on how the panic propagates through the runtime executor, risks halting block production for the affected chain — matching the "route unable to deliver messages" / DoS impact category explicitly in scope.

### Likelihood Explanation
Likelihood is high for any relayer-facing deployment of `pallet-hyper-fungible-token`: any address able to call the source-chain `send()` function with a non-empty calldata field can craft the payload, no privileged role or governance action is required, and the vulnerable decode is unconditionally reached whenever `message.data` is non-empty and successfully parses as `SubstrateCalldata` — a low-cost, single-transaction trigger.

### Recommendation
Mirror `pallet-call-decompressor`'s mitigation: decode `substrate_data.runtime_call` with `T::RuntimeCall::decode_all_with_depth_limit(MAX_DEPTH, &mut &*substrate_data.runtime_call)` using an explicit, conservative depth bound (and reject trailing bytes via `decode_all`), instead of a bare `Decode::decode` call, before running `BaseCallFilter` and dispatching.

### Proof of Concept
1. On the source EVM/Substrate chain, call `HyperFungibleToken.send()` (or the substrate-side equivalent) with a valid token transfer and a `data` payload equal to a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <bytes> }`, where `<bytes>` is a `RuntimeCall` nested hundreds/thousands of levels deep (e.g. `Sudo(sudo(Sudo(sudo(...System::remark...))))`, following the exact construction used in the project's own `decompress_stack_exhaustion_poc` test) [10](#0-9) .
2. Once the message is relayed and `pallet-hyper-fungible-token::on_accept` is invoked on the destination chain, the token mint/transfer succeeds, then `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` is reached at [5](#0-4)  with no depth cap applied by this pallet, unlike the protected `pallet-call-decompressor` path.
3. Observe decode-time resource exhaustion/crash on the destination node processing this message, versus the guarded `ErrorDecodingCall` rejection that the same nested-call construction produces when routed through `pallet-call-decompressor`'s `decode_all_with_depth_limit`.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L120-122)
```rust
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L176-200)
```rust
			} else {
				let from_bytes = message.from.as_ref();
				if source.is_evm() {
					T::EvmToSubstrate::convert(H160::from_slice(
						&from_bytes[from_bytes.len() - 20..],
					))
				} else {
					let mut account = [0u8; 32];
					account.copy_from_slice(from_bytes);
					account.into()
				}
			};

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
