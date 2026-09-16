## Title
Unbounded-depth `RuntimeCall` deserialization in `pallet-hyper-fungible-token`'s cross-chain calldata execution enables stack-overflow DoS - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
The H2O-3 CVE is a "trust the wire format, dispatch it" bug: an attacker-controlled, insufficiently validated serialized blob is decoded and acted on by a privileged code path, leading to RCE. The closest reachable analog in this codebase is `pallet-hyper-fungible-token`'s `on_accept` handler, which SCALE-decodes an attacker-supplied `RuntimeCall` byte blob (embedded in the cross-chain `Message.data` field) using the unbounded `Decode::decode` and then dispatches it, whereas the *only other* pallet in this repo that performs the same operation (`pallet-call-decompressor`) explicitly hardens this exact decode against recursion-based stack exhaustion.

### Finding Description
`Pallet::<T>::on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs` decodes the optional cross-chain calldata attached to an incoming token transfer: [1](#0-0) 

and later decodes the embedded `runtime_call` bytes directly into the runtime's full `RuntimeCall` enum with the plain, non-depth-limited decoder before dispatching it as a signed/derived origin: [2](#0-1) 

`substrate_data.runtime_call` is fully attacker-controlled: any unprivileged caller can trigger a cross-chain `send()` on the paired `HyperFungibleToken`/`WrappedHyperFungibleToken` EVM (or substrate) contract with an arbitrary `data` payload, as documented in the SDK docs: [3](#0-2) 

Once relayed, this payload reaches `on_accept` on the destination chain and is decoded with `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` — a plain `codec::Decode::decode`, not `decode_all_with_depth_limit`.

By contrast, `pallet-call-decompressor`, the other pallet in this repo that decodes an untrusted, fully-attacker-controlled `RuntimeCall` byte string before dispatch, explicitly wraps the decode with a recursion-depth guard and documents why: [4](#0-3) [5](#0-4) 

The `hyper-fungible-token` module has no equivalent guard. If the runtime's `RuntimeCall` enum contains recursively-nestable variants (e.g. `Utility::batch`, `Proxy::proxy`, nested `Vec<Call>` structures common in Substrate runtimes), an attacker can hand-craft a deeply nested SCALE encoding that recurses through the derived `Decode` implementation far enough to exhaust the collator/validator's stack, panicking the node process — the same class of "improperly validated serialized structure reaches unsafe processing" root cause as the reported CVE, just manifesting as node-crash/DoS rather than RCE given Rust's memory safety.

### Impact Explanation
A successful exploit crashes the node process executing the extrinsic (collator/validator), which is reachable via a normal, permissionless cross-chain token transfer — no privileged role required. Repeated submission from any account holding minimal bridge tokens can be used to repeatedly crash block producers processing ISMP messages for this pallet, which is a liveness/DoS impact on the chain — “a route unable to deliver messages” per the validation criteria, since the pallet handling incoming HFT messages becomes unusable/crash-prone.

### Likelihood Explanation
Likelihood depends on whether the target runtime's `RuntimeCall` type actually contains deeply-nestable variants (e.g. via `pallet-utility`, `pallet-proxy`, or similar batching primitives) that are also not excluded by `BaseCallFilter`. Given Hyperbridge's parachain runtimes (`gargantua`, `nexus`) are typical Substrate runtimes, such variants are plausible but not confirmed in the reachable scope of this investigation; the underlying missing-depth-limit issue itself is nonetheless concretely present and inconsistent with the hardened sibling code path.

### Recommendation
Replace `T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)` in `modules/pallets/hyper-fungible-token/src/module.rs` with `T::RuntimeCall::decode_all_with_depth_limit(MAX_DEPTH, &mut &*substrate_data.runtime_call)` using the same bounded depth constant pattern established in `pallet-call-decompressor`, and audit any other pallet that decodes attacker-supplied `RuntimeCall`/nested-enum bytes for the same gap.

### Proof of Concept
1. On a source chain, call `HyperFungibleToken.send()` (or the substrate pallet's `send` extrinsic) with `data` set to a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <crafted bytes> }`, where `<crafted bytes>` is a deeply/recursively nested encoding of a `RuntimeCall` variant that supports nesting (e.g. repeated `Utility::batch([Utility::batch([...])])`) to a depth sufficient to exhaust stack space.
2. Have the message relayed cross-chain to a destination chain running `pallet-hyper-fungible-token`.
3. `on_accept` reaches `SubstrateCalldata::decode` then `T::RuntimeCall::decode(...)` at line 189 without a depth limit, causing the collator/validator processing the block to attempt deep recursive decoding and crash/panic.

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

**File:** docs/content/developers/polkadot/hyper-fungible-token.mdx (L202-216)
```text
## Calldata Execution

The `call_data` field in `SendParams` allows executing arbitrary runtime calls on the destination substrate chain after the tokens are transferred. The calldata is SCALE-encoded as:

```rust lineNumbers
pub struct SubstrateCalldata {
    /// Optional SCALE-encoded MultiSignature of (account_nonce, runtime_call)
    pub signature: Option<Vec<u8>>,
    /// SCALE-encoded runtime call to execute
    pub runtime_call: Vec<u8>,
}
```

If a signature is provided, it is verified against the beneficiary's account nonce and the runtime call before dispatch. Supported signature types: Ed25519, Sr25519, ECDSA. The account nonce is incremented after dispatch to prevent replay.

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
