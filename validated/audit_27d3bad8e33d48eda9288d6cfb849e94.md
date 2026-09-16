### Title
Unchecked length panic in `HyperFungibleToken::on_accept` when deriving the calldata-execution origin from `message.from` - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::<T>::on_accept` (the ISMP module handler invoked for every accepted `PostRequest` delivered to the hyper-fungible-token pallet) derives the dispatch origin for optional cross-chain calldata from `message.from` without validating its byte length before performing a fixed-size slice/copy, mirroring the CVE-2019-9640 pattern of reading a length-controlled field without a bounds check before a fixed-width read.

### Finding Description
In the unsigned-calldata branch of `on_accept`: [1](#0-0) 

```rust
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
```

`message` is the result of `Message::abi_decode(&body)` where `body` is the raw `PostRequest.body` — attacker/relayer-controlled payload delivered over ISMP and only authenticated by the `(source, from)` → asset-id lookup in `ContractToAsset`, not by any length constraint on the embedded `from` field: [2](#0-1) 

Unlike `message.to`, which is explicitly length-checked before use (32 or 20 bytes, else a typed error): [3](#0-2) 

`message.from` is used directly with no such guard, in the branch that only runs when calldata is present and unsigned (`substrate_data.signature` is `None`):

- If `source.is_evm()` and `from_bytes.len() < 20`, the expression `from_bytes.len() - 20` underflows a `usize` subtraction, which panics on overflow checks (debug/checked builds) or produces an enormous index on release builds — in either case the subsequent slice indexing panics with an out-of-bounds/invalid read, analogous to the unchecked length read in `exif_process_SOFn`.
- If `!source.is_evm()` and `from_bytes.len() != 32`, `copy_from_slice` panics on any length mismatch (both too short and too long), again an unchecked-length read/write into a fixed-size buffer.

This is reachable by any relayer/token bridger delivering a `PostRequest` through `pallet_ismp::handle_unsigned` whose ABI-decoded `Message.data` is non-empty and whose `SubstrateCalldata.signature` is absent, provided the message ultimately resolves to a valid `(source, from)` → asset mapping (i.e., is otherwise a legitimate-looking bridged mint) but the `from` field itself is not length-checked before this final origin-derivation step.

### Impact Explanation
A panic reached from inside `IsmpModule::on_accept`, invoked from the on-chain unsigned message-execution path (`pallet_ismp::Pallet::execute` → `handle_unsigned`), propagates as a runtime panic during block execution rather than a graceful `DispatchError`. This can halt/crash block production for the parachain processing the message (denial of service on message delivery for this route), which under the scoring rubric qualifies as "a route unable to deliver messages" — impacting not just this pallet's messages but the entire block's other extrinsics that would have executed in the same block.

### Likelihood Explanation
Reaching this code requires: (1) a registered `ContractToAsset` mapping for `(source, from_bytes)` matching a legitimate source contract/asset pairing, and (2) a `Message.data` payload that decodes to `SubstrateCalldata` with no `signature`. Both conditions are plausible for a bridged token transfer that also carries calldata (a supported, advertised feature), and the length of `message.from` inside the ABI-decoded `Message` is controlled by whatever encoded the cross-chain `body` — if `from` is a dynamic `bytes` field (as the branch on `source.is_evm()` suggests, since it must support multiple source-chain address widths), its length is not fixed at the ABI-decode layer and this path is directly triggerable by anyone able to originate or relay such a message.

### Recommendation
Validate `from_bytes.len()` explicitly before use, mirroring the existing `to_bytes` check, and return a typed `HftError` (e.g. `InvalidRecipientLength`/a new `InvalidSenderLength`) instead of panicking:
```rust
let from_bytes = message.from.as_ref();
let origin_account = if source.is_evm() {
    if from_bytes.len() != 20 {
        Err(HftError::InvalidSenderLength(from_bytes.len()))?;
    }
    T::EvmToSubstrate::convert(H160::from_slice(from_bytes))
} else {
    if from_bytes.len() != 32 {
        Err(HftError::InvalidSenderLength(from_bytes.len()))?;
    }
    let mut account = [0u8; 32];
    account.copy_from_slice(from_bytes);
    account.into()
};
```

### Proof of Concept
1. Register a valid `ContractToAsset` mapping for `(source, from)` where `from` is deliberately encoded as e.g. 5 bytes (permitted if `Message.from` is ABI type `bytes`).
2. Craft a `Message.data` that decodes to `SubstrateCalldata { signature: None, runtime_call: <any> }`.
3. Deliver this as a `PostRequest.body` through `pallet_ismp::handle_unsigned`.
4. Execution reaches the `else` branch (no signature) in `on_accept`; since `source.is_evm()` is true and `from_bytes.len() == 5 < 20`, `from_bytes.len() - 20` underflows, panicking the runtime during block execution instead of returning a `DispatchError`.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-59)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L63-71)
```rust
		let mut beneficiary_bytes = [0u8; 32];
		let to_bytes = message.to.as_ref();
		if to_bytes.len() == 32 {
			beneficiary_bytes.copy_from_slice(to_bytes);
		} else if to_bytes.len() == 20 {
			beneficiary_bytes[12..].copy_from_slice(to_bytes);
		} else {
			Err(HftError::InvalidRecipientLength(to_bytes.len()))?;
		}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L176-186)
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
```
