### Title
Unchecked-length `copy_from_slice` panic in HFT `on_accept` substrate-calldata origin resolution - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::<T>::on_accept` decodes a cross-chain `Message` from an ISMP `PostRequest` body and, when the message carries calldata with no signature, copies the raw `message.from` bytes into a fixed `[u8; 32]` buffer without validating the length first. Unlike the sibling `on_timeout` handler in the same file, which explicitly checks for 32- or 20-byte lengths before calling `copy_from_slice`, this path performs the copy unconditionally, and any `from` field whose byte length is not exactly 32 causes a Rust panic/wasm trap.

### Finding Description
In `on_accept`: [1](#0-0) 

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

`from_bytes` comes straight from `message.from`, an ABI-decoded field of the attacker-controlled `body` passed to `on_accept`: [2](#0-1) 

The `beneficiary_bytes` conversion just above (`to` field) correctly checks length (32 or 20 bytes) before copying and returns a typed error otherwise: [3](#0-2) 

The `on_timeout` handler for the *same* `Message.from` field applies the identical length check before copying: [4](#0-3) 

But the `on_accept` calldata-origin branch (used when `source.is_evm()` is false, i.e. the source is a Substrate-style chain, and the message carries `data` with no `signature`) skips this check entirely. `Vec<u8>::copy_from_slice` requires the destination and source slices to have equal length and panics otherwise — this is exactly the same bug class as the underlying CVE (buffer write sized against an unchecked attacker-supplied length, from `doc_common.c`'s DOCXWRITE/TXTWRITE text buffer overflow): a fixed-size destination buffer receiving attacker-controlled variable-length data without a length gate.

Because `PostRequest.body` (and therefore `message.from`) is fully controlled by whoever dispatches the cross-chain ISMP message (any unprivileged relayer/dispatcher delivering a message to a registered HFT source contract, subject only to `ContractToAsset` lookup succeeding), an attacker who has a live source-contract/asset mapping can craft a `from` value of any length ≠ 32 to trigger this panic.

The reproducible codebase pattern of previously-fixed panics on this exact CVE-class bug (`modules/utils/serde/src/lib.rs`, `modules/ismp/core/src/host.rs::FromStr`, `parachain/node/fisherman/src/lib.rs`, `tesseract/consensus/beefy/src/prover.rs`, `tesseract/consensus/parachain/src/lib.rs`) all guard length before `copy_from_slice`; this call site was missed.

### Impact Explanation
A panic inside `on_accept`, which runs during ISMP request-handling dispatch (`pallet-ismp` message execution / `handle_unsigned` extrinsic processing), traps the runtime execution. In a Substrate/FRAME runtime, an unhandled panic inside pallet dispatch logic aborts the executing block-building/import worker (the same failure mode documented in the fixed `as_utf8_string` case, which "took the process down"). This is reachable from a single relayed message with no privileged access required, and can be repeated to deny message delivery for the HFT bridge route — a "route unable to deliver messages" condition matching the accepted-impact criteria. It does not directly mint/burn funds, but it is a denial-of-service on the token-bridge message-handling path triggerable by any party able to get a message accepted by `ContractToAsset` lookup for a registered source contract.

### Likelihood Explanation
High: no special privileges or timing are needed. Any account able to relay/deliver an ISMP `PostRequest` whose `source`/`from` pair matches an already-configured `ContractToAsset` entry, and whose ABI-decoded `Message.data` is non-empty with `substrate_data.signature == None`, can set `message.from` to an arbitrary byte string. Only three preconditions gate exploitation: `source.is_evm() == false` (the source state machine is registered as non-EVM in this deployment), a valid `ContractToAsset` mapping exists, and `message.data` decodes to `SubstrateCalldata` with no signature — none of which require an unusual on-chain state, since asset mappings are ordinary configuration for any Substrate-based HFT deployment that accepts cross-chain calldata execution.

### Recommendation
Mirror the length check already used for `beneficiary_bytes` (lines 63–71) and in `on_timeout` (lines 226–230): validate `from_bytes.len() == 32` (or handle the 20-byte EVM case explicitly) and return a typed `HftError` (e.g., reuse/extend `HftError::InvalidRecipientLength`) instead of calling `copy_from_slice` unconditionally.

### Proof of Concept
1. Deploy/identify an HFT deployment where a `ContractToAsset` mapping exists for `(source, from_contract)` with `source.is_evm() == false` (e.g. a Substrate-to-Substrate HFT bridge lane).
2. Craft an ISMP `PostRequest` whose ABI-decoded `body` yields a `Message` with:
   - `data` = SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <any allowed call> }`
   - `from` = any byte sequence whose length is not 32 (e.g. 31 or 33 bytes)
3. Relay/deliver the message so `pallet_ismp` invokes `Pallet::<T>::on_accept` on it (no signature/authorization on the message content itself is required beyond normal relayer message delivery).
4. Execution panics at `account.copy_from_slice(from_bytes)` in `modules/pallets/hyper-fungible-token/src/module.rs:184`, trapping the runtime call and halting block execution/import for that operation.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-72)
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
		let beneficiary: T::AccountId = beneficiary_bytes.into();
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L218-230)
```rust
	fn on_timeout(&self, request: Request) -> Result<Weight, anyhow::Error> {
		match request {
			Request::Post(PostRequest { body, to, dest, .. }) => {
				let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;

				// Refund the original sender
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
```
