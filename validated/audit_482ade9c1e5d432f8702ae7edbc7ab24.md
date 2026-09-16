Found the analog. This is the strongest reachable hit for the CVE-2016-8596 bug class (unchecked attacker-controlled length feeding a fixed-size buffer copy).

### Title
Unchecked-length `message.from` panics `on_accept` via fixed-size buffer copy - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`Pallet::on_accept` in the `hyper-fungible-token` pallet decodes an ABI-encoded `Message` from an incoming ISMP `PostRequest.body` and, when optional calldata carries no signature, converts `message.from` into a substrate `AccountId` by either slicing `from_bytes[from_bytes.len() - 20..]` (EVM source) or `copy_from_slice` into a fixed `[0u8; 32]` (non-EVM source) — neither branch validates the length of `from_bytes` first, unlike the sibling `to_bytes` handling a few lines above which explicitly checks for 32/20 bytes and errors otherwise.

### Finding Description
`on_accept` is the `IsmpModule` callback invoked when a relayer delivers a proven cross-chain `PostRequest` addressed to this pallet. `message.from` is an attacker/source-app-controlled ABI `bytes` field embedded in the request body (not a fixed-width chain identity field validated by the host): [1](#0-0) 

Compare this to the `to_bytes` handling just above it, which is properly length-checked and errors cleanly for any other length: [2](#0-1) 

For `message.from`:
- EVM branch: `&from_bytes[from_bytes.len() - 20..]` — if `from_bytes.len() < 20`, the subtraction underflows (`usize`), producing either a panic (debug) or a massive out-of-range slice index that panics on the range-check (release), since Rust always bounds-checks slice indexing even in release mode.
- Non-EVM branch: `account.copy_from_slice(from_bytes)` where `account: [0u8; 32]` — `copy_from_slice` asserts `from_bytes.len() == 32` and panics otherwise.

This path is only reached when `message.data` is non-empty and carries `SubstrateCalldata` with no `signature` field, which is entirely attacker-controlled ABI-encoded data inside the cross-chain message body. A relayer delivering a legitimately-proven ISMP message (the proof only attests to the message's inclusion/commitment, not to the semantic validity of `message.from`'s length) can trivially construct a `from` field of any length, since it is just ABI `bytes`.

This mirrors the root cause class of CVE-2016-8596: attacker-controlled length data is copied into/indexed against a fixed-size buffer without a length check, whereas the analogous field (`to_bytes`) in the same function correctly validates length first.

### Impact Explanation
A successful trigger causes a Rust panic inside `on_accept`, which executes in the runtime's message-dispatch path for `pallet-ismp`/`pallet-hyper-fungible-token`. A panic during block execution halts/traps that transaction's execution context; depending on how `IsmpModule::on_accept` errors propagate through `pallet-ismp`'s dispatch machinery, an unrecovered panic in an unsigned or relayer-submitted extrinsic can disrupt block production or force a `pallet-ismp` message batch to fail non-gracefully instead of being cleanly rejected — a denial-of-service against the token-bridge message-delivery path. Because the panic path is reached only after the pallet has already executed the mint/transfer of the token amount to `beneficiary` (steps at lines 93–117 execute before this from-decoding code at line 119+), a relayer who can force a panic *after* funds have moved could be used to disrupt the surrounding transaction's finalization or event emission depending on runtime panic-handling semantics, though the primary confirmed impact is an availability/DoS break of the deliver-and-execute path for the optional-calldata feature — a route where a message cannot be delivered/executed as intended.

### Likelihood Explanation
High: the only precondition is that `message.data` is non-empty and `SubstrateCalldata::signature` is `None`, both attacker-controlled ABI fields inside the message body, and that `message.from` (also attacker-controlled ABI bytes independent of `source`/`from` protocol-level fields) is set to any length other than 20 (EVM source) or 32 (non-EVM source). Any account able to dispatch a POST request to a registered `HyperFungibleToken`/`WrappedHyperFungibleToken` contract can encode such a payload; no privileged role is required.

### Recommendation
Validate `from_bytes.len()` before use, mirroring the existing `to_bytes` pattern: for the EVM branch require `from_bytes.len() == 20` (or safely handle longer values without underflowing, e.g. via `checked_sub`/explicit length check) and return `HftError::InvalidRecipientLength`-style error instead of panicking; for the non-EVM branch require `from_bytes.len() == 32` and return an error otherwise instead of calling `copy_from_slice` unchecked.

### Proof of Concept
1. Register a `HyperFungibleToken` mapping for some `source`/`from` (chain contract) pair so `ContractToAsset` resolves.
2. From the registered source contract, dispatch a POST request whose ABI-encoded body is a `Message { from: bytes, to: bytes(20 or 32), amount: uintN, data: bytes }` where:
   - `to` is a valid 20 or 32-byte recipient (so the earlier check passes),
   - `data` is non-empty and SCALE-decodes to `SubstrateCalldata { signature: None, runtime_call: <any valid call> }`,
   - `message.from` (the *inner* ABI field, independent of the ISMP-level `from`) is set to a byte string of length e.g. 5 bytes.
3. Relay this proven request to the destination chain's `on_accept`. When `source.is_evm()` is true, execution reaches `&from_bytes[from_bytes.len() - 20..]` with `from_bytes.len() == 5`, causing `5usize - 20` to underflow and the subsequent slice index to panic; on a non-EVM `source`, setting `message.from` to any length other than 32 reaches `account.copy_from_slice(from_bytes)` and panics on the length mismatch assertion. [3](#0-2)

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
