### Title
Unbounded recursive `RuntimeCall` decode in hyper-fungible-token cross-chain calldata causes stack-exhaustion DoS - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::<T>::on_accept` in the hyper-fungible-token ISMP module decodes an attacker-supplied `RuntimeCall` from cross-chain token-transfer calldata with plain `Decode::decode`, with no recursion-depth limit, unlike the sibling `pallet-call-decompressor` module which was hardened against exactly this bug class with `decode_all_with_depth_limit` after a documented stack-exhaustion PoC.

### Finding Description
When an HFT (`hyper-fungible-token`) `PostRequest` is accepted via `on_accept`, the module ABI-decodes the message body and, if `message.data` is non-empty, decodes it as `SubstrateCalldata` and then decodes the embedded `runtime_call` bytes directly: [1](#0-0) [2](#0-1) 

`T::RuntimeCall::decode(...)` is a plain SCALE `Decode::decode` call with **no depth limit**. `RuntimeCall` is a recursive enum: it contains variants that box other `RuntimeCall`s (e.g. `pallet_sudo::Call::sudo { call: Box<RuntimeCall> }`, `pallet_utility::Call::batch { calls: Vec<RuntimeCall> }`, `pallet_proxy::Call::proxy { call: Box<RuntimeCall> }`). The SCALE codec's recursive-enum decoder consumes native stack frames per nesting level with no bound, exactly the bug class described in CVE-2017-12595 (QPDF's recursive tokenizer for nested arrays/dictionaries causing stack exhaustion on deeply nested untrusted input).

The codebase already recognizes and fixes this exact bug class elsewhere:
- `pallet-call-decompressor` decodes `RuntimeCall` with an explicit `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT` via `decode_all_with_depth_limit`, with a regression test (`decompress_stack_exhaustion_poc`) that documents a 1000-level nested `Sudo(sudo(...))` PoC: [3](#0-2) [4](#0-3) [5](#0-4) 
- Similarly, `modules/consensus/pharos/primitives/src/spv.rs` bounds proof-walk recursion with `MAX_PROOF_DEPTH` after a documented stack-overflow regression, and `modules/trees/ethereum/src/node_codec.rs` was hardened against a panic on adversarial empty HP-encoded partial keys.

The HFT module's `runtime_call` decode was missed when this class of fix was applied elsewhere, leaving an unbounded recursive decode reachable from cross-chain, attacker-controlled message content.

### Impact Explanation
`on_accept` is invoked as part of normal ISMP message delivery (`pallet_ismp::Call::handle_unsigned`), which is dispatched as an **unsigned** extrinsic executed by every node that validates and imports the block, including during transaction-pool validation (`ValidateUnsigned::validate_unsigned` also calls `Self::execute`, which reaches `on_accept`). A crafted deeply-nested `RuntimeCall` inside the calldata of a legitimate-looking cross-chain token transfer (with valid HFT/ISMP proof from any connected source chain the attacker controls or can post from) will overflow the call stack during decode on every relayer/collator/full node that processes the message — in the mempool validation path this happens before the message is even included in a block, and in block execution it happens deterministically for all validating nodes. This can crash node processes network-wide, i.e. a route/chain unable to deliver or validate messages — a denial-of-service on message delivery, which is in scope per the "route unable to deliver messages" impact criterion.

### Likelihood Explanation
Likelihood is high: any account able to dispatch a cross-chain HFT transfer with calldata (a permissionless, unprivileged action for a "token bridger") can embed an arbitrarily deep nested `RuntimeCall` (e.g., via `Sudo::sudo`, `Utility::batch`, or `Proxy::proxy`, which are commonly present in Substrate runtimes) inside `substrate_data.runtime_call`. No special privileges, governance, or malicious node/collator/prover access is required — only a normal token-transfer message with attacker-chosen calldata bytes, reaching a codepath (`on_accept`) directly invoked from ISMP request handling.

### Recommendation
Replace the plain `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` call with a depth-limited decode (e.g. `codec::DecodeLimit::decode_all_with_depth_limit` or `decode_with_depth_limit`), mirroring the fix already applied in `pallet-call-decompressor`, with a limit sized to the minimum nesting genuinely required for supported calls. Apply the same treatment to any other `Decode::decode` call sites for recursive/`Box`-containing types reachable from untrusted cross-chain message bodies (e.g. `SubstrateCalldata::decode`, `MultiSignature::decode` if applicable to nested structures).

### Proof of Concept
1. On the source EVM chain, initiate an HFT token transfer whose `data` field is a `SubstrateCalldata { signature: None, runtime_call: <bytes> }` where `<bytes>` is the SCALE encoding of `RuntimeCall::Sudo(pallet_sudo::Call::sudo { call: Box::new(RuntimeCall::Sudo(pallet_sudo::Call::sudo { call: Box::new(...) })) })` nested thousands of levels deep (analogous to the existing `decompress_stack_exhaustion_poc` test's construction at [6](#0-5) , but sent as HFT calldata instead of a compressed call).
2. Relay the resulting ISMP `PostRequest` with a valid consensus/state proof to the destination chain running the HFT pallet.
3. When the destination node executes `handle_unsigned` (or validates it as an unsigned transaction in the pool), `Pallet::<T>::on_accept` reaches `T::RuntimeCall::decode(...)` at `modules/pallets/hyper-fungible-token/src/module.rs:189`, which recurses once per nesting level with no limit, exhausting the stack and crashing/panicking the node process — reproducing the same failure mode the `decompress_stack_exhaustion_poc` test was written to prevent, but through an unguarded codepath.

### Citations

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
