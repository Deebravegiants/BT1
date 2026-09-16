Confirmed: `Message.from` is an arbitrary-length `bytes` field (`alloy_sol_types` dynamic bytes, see `token_message = Message { from: sender.to_vec().into(), ... }` in `modules/pallets/hyper-fungible-token/src/lib.rs:298`), so when this pallet receives an EVM-originated post (i.e. an incoming `HyperFungibleToken.sol` message), the length of `message.from` is fully controlled by whoever calls the source-chain contract's send function — it is not fixed at 20 bytes and is never length-checked on the receiving side.

### Title
Integer underflow in `hyper-fungible-token::on_accept` calldata-origin derivation causes an unbounded-length slice panic - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` derives the calldata-dispatch origin from the untrusted, ABI-decoded `Message.from` field. When the request carries optional `data` and no `signature`, and the source chain is EVM, the code computes `from_bytes.len() - 20` to strip an address out of `from_bytes` without first checking that `from_bytes.len() >= 20`.

### Finding Description
`on_accept` decodes the incoming ISMP `PostRequest.body` into a `Message` struct with `Message::abi_decode` [1](#0-0) . `Message.from` is a dynamic `bytes` field whose length is chosen by the caller of the source-chain contract, exactly as it is populated on the outbound path with `from: sender.to_vec().into()` [2](#0-1) . Nothing constrains this field's length to 20 or 32 bytes on decode.

When `message.data` is non-empty and the embedded `SubstrateCalldata` carries no signature, the module falls back to deriving the dispatch origin directly from `message.from`: [3](#0-2) 
If `source.is_evm()` is true, it computes `&from_bytes[from_bytes.len() - 20..]`. If an attacker supplies `message.from` shorter than 20 bytes, `from_bytes.len() - 20` underflows the `usize`, wrapping to a huge value; the subsequent slice index then panics with an out-of-range error. This mirrors the CVE's root cause pattern: a small, attacker-chosen length field feeding directly into an unchecked subtraction that is expected to always be "big enough," causing a low-level memory-safety fault (in Rust, an immediate panic/trap rather than silent corruption, since slice indexing is bounds-checked) — but reachable identically: a hostile short-length input crashes execution before any authentication of the derived origin.

Note that authentication of the *sender contract* (`ContractToAsset::get(source, &from)` at [4](#0-3) ) uses the outer ISMP `PostRequest.from`, which is a different field from the inner `message.from` decoded from the body — so validating the outer field does nothing to bound the inner one.

### Impact Explanation
This is reachable by any account able to call the registered `HyperFungibleToken`/`WrappedHyperFungibleToken` contract on a connected EVM chain and attach calldata (`message.data`) with an unsigned `SubstrateCalldata` while setting `from` to fewer than 20 bytes. The resulting panic occurs inside `on_accept`, which is invoked from the ISMP message-handling path (`pallet_ismp::Pallet::execute` / `handle_unsigned`). A panic here is not a graceful `Result::Err` — it unwinds through code that expects only `Result`, and depending on how `pallet-ismp` handles module-handler panics, it can abort processing of the batch, effectively letting a single relayed message halt processing of that dispatch (a "route unable to deliver messages" outcome), and at minimum guarantees the message itself and any batched requests cannot be delivered, which can be used to grief relayers or freeze in-flight deliveries for that batch.

### Likelihood Explanation
High: This is a single-transaction condition purely under the control of the party invoking the source-chain bridge contract, requires no privileged role, no consensus forgery, and no race condition — only a `from` field shorter than 20 bytes plus non-empty `data`. Overflow-checked builds panic deterministically; even without overflow checks, the wrapped value still causes a bounds-check panic on the subsequent slice.

### Recommendation
Validate `from_bytes.len() >= 20` (and `== 20` for EVM sources, `== 32` for substrate sources, mirroring the existing `to_bytes` length validation used for `beneficiary_bytes` at [5](#0-4) ) before slicing, returning a typed `HftError` (e.g. `InvalidSenderLength`) instead of panicking.

### Proof of Concept
1. On the source EVM chain, call the registered `HyperFungibleToken` contract's send function with a `Message.from` of length 0–19 bytes, a non-empty `data` payload containing a valid `SubstrateCalldata` (with `signature: None`), and a normal `to`/`amount`.
2. Relay the resulting request to the Hyperbridge parachain; `pallet_ismp` invokes `HftPallet::on_accept`.
3. Execution reaches `let from_bytes = message.from.as_ref(); ... &from_bytes[from_bytes.len() - 20..]` [6](#0-5)  with `from_bytes.len() < 20`, underflowing the subtraction and panicking on the subsequent out-of-range slice.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L55-56)
```rust
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-59)
```rust
		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L64-71)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L293-302)
```rust
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

			let token_message = Message {
				from: sender.to_vec().into(),
				to: params.recipient.to_vec().into(),
				amount: alloy_primitives::U256::from_be_bytes(erc20_amount.to_big_endian()),
				data: params.call_data.unwrap_or_default().into(),
			};
```
