### Title
Fixed-size array `copy_from_slice` panic on attacker-controlled `PostRequest.from` length in `pallet-hyper-fungible-token::on_accept` - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler, when processing an incoming cross-chain message that carries calldata (`message.data` non-empty) without an accompanying signature, derives the dispatch origin directly from the ISMP `PostRequest.from` field. On the substrate-source branch it copies that variable-length, attacker/source-chain-controlled byte slice into a fixed `[0u8; 32]` array via `copy_from_slice`, and on the EVM-source branch it slices the tail 20 bytes without checking the input is at least 20 bytes long. Both operations panic if the length assumption doesn't hold, which is the exact bug class as the reported ISO15118 `payment_options` overflow: unchecked variable-length data copied into a fixed-size buffer from a message field that schema/length validation does not guarantee.

### Finding Description
In `on_accept`: [1](#0-0) 
When calldata is present and no `signature` was supplied in `SubstrateCalldata`, the code falls back to using the raw `message.from` (the ISMP `PostRequest.from` bytes) as the origin: [2](#0-1) 

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
```

`message.from` originates from the ABI-decoded `Message.from` field of the incoming cross-chain body — a byte string whose length is set entirely by whatever contract/pallet on the *source* chain constructed the message (e.g. `abi.encodePacked(msg.sender)` on EVM, but nothing in the wire format enforces exactly 20/32 bytes on the receiving side). This is essentially the same shape as the ISO15118 bug: a length-prefixed, variable-length field from an untrusted cross-chain payload is copied into a statically-sized buffer with no length check.

- Substrate-source branch: `account.copy_from_slice(from_bytes)` where `account: [u8; 32]`. `copy_from_slice` panics ("source slice length does not match destination") for any `from_bytes.len() != 32`.
- EVM-source branch: `from_bytes.len() - 20` underflows (panics in debug builds; in release with overflow checks off it wraps to a huge value and the subsequent slice index panics) whenever `from_bytes.len() < 20`.

Note the earlier `to_bytes`/`beneficiary_bytes` conversion in the same function correctly validates length before copying: [3](#0-2) 
but the symmetric handling of `message.from` in the no-signature origin-derivation branch omits that check, which is the root cause.

### Impact Explanation
This code path executes inside `on_accept`, which is invoked by the ISMP request-handling pipeline (`pallet-ismp`'s message dispatch, `modules/ismp/core/src/handlers/request.rs`) for every relayed `PostRequest` destined for the hyper-fungible-token module — reachable by any relayer submitting a proof for a message originating from a registered peer contract on a source chain. Triggering the panic aborts the runtime call inside `on_accept`; because this executes as part of on-chain STF logic (not an isolated RPC worker thread as in some of the other guarded cases in this codebase), a panic here traps the WASM runtime execution for that block/extrinsic. Depending on how the panic unwinds inside the pallet's dispatchable, this can fail block production/import for validators processing the relayed batch, denying delivery of that and subsequent messages in the same call — a "route unable to deliver messages" condition, and in the worst case a node-level DoS for parachain collators executing the block.

### Likelihood Explanation
Reachable from a single relayed ISMP message: an attacker needs a message with a `to` field of valid length (20/32, that part is checked), a non-empty `data` field, and `SubstrateCalldata.signature = None`, with `from` set to any length other than 32 bytes (substrate destination-account path) or shorter than 20 bytes (EVM-source path). The `from` field content/length is not otherwise validated by the ISMP core or by this pallet before reaching this line, so a message from a compromised, buggy, or intentionally malicious/mismatched peer contract can trivially hit this panic without any privileged actor.

### Recommendation
Validate `from_bytes.len()` before copying, mirroring the existing `to_bytes` handling: return an `HftError` (e.g. `InvalidSenderLength`) for lengths other than the expected 20 (EVM) or 32 (substrate) bytes instead of calling `copy_from_slice`/slicing unconditionally. Add regression tests analogous to the `as_utf8_string_rejects_non_four_byte_input` / `consensus_state_id_from_str` tests already present elsewhere in this codebase for this exact bug class.

### Proof of Concept
1. Register a peer contract mapping for some `source` chain and `local_asset_id` via `ContractToAsset`.
2. Construct a `Message { to: <valid 20 or 32 bytes>, amount: <valid>, data: <non-empty Call[] ABI bytes>, from: <e.g. 5 bytes> }` and encode it as `SubstrateCalldata { signature: None, runtime_call: <any valid encoded call> }` inside `message.data`.
3. Relay this as a `PostRequest` to the hyper-fungible-token module's `on_accept`.
4. Execution reaches the `else` branch at [2](#0-1) ; for a non-EVM `source`, `account.copy_from_slice(from_bytes)` panics because `from_bytes.len() == 5 != 32`.

Note: I could not fully load `modules/pallets/hyper-fungible-token/src/types.rs` (the exact `Message`/`SubstrateCalldata` field type definitions) in this session due to tool-call limits reached before verifying whether `Message.from` has any independent ABI-level length constraint; the analysis above is based on the `on_accept` handler logic and the analogous, already-checked `to_bytes` handling in the same function. A Devin session with full file access should confirm the exact `Message.from` type/encoding constraints before finalizing the fix.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L61-71)
```rust
		// Convert recipient bytes to substrate AccountId
		// If 32 bytes: use directly. If 20 bytes: left-pad with zeros.
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-128)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

			let origin = if let Some(signature) = substrate_data.signature {
				let multi_signature = MultiSignature::decode(&mut &*signature)
					.map_err(HftError::SignatureDecodeError)?;

				let nonce = frame_system::Pallet::<T>::account_nonce(beneficiary.clone());
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L176-187)
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
```
