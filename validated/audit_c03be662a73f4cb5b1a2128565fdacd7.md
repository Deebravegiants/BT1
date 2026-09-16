### Title
Unvalidated ABI-decoded `Message.from` length causes runtime panic in `pallet-hyper-fungible-token::on_accept` - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
The ALPINE-CVE-2017-17997 bug class is: a dissector trusts an untrusted field's shape/length and dereferences/indexes it without validation, crashing the process. The same pattern exists in `pallet-hyper-fungible-token`'s ISMP module handler: `message.from`, a dynamic `bytes` field decoded straight out of the attacker/relayer-delivered request body via `Message::abi_decode(&body)` [1](#0-0) , is used unchecked in the `on_accept` calldata-execution fallback path, unlike every sibling use of a length-variable field in the same file.

### Finding Description
`on_accept` validates `message.to` before using it (`to_bytes.len() == 32` or `20`, else a typed `InvalidRecipientLength` error) [2](#0-1) , and `on_timeout` validates `message.from` the same way (`InvalidSenderLength` on any other length) [3](#0-2) .

However, when `on_accept` executes optional destination-chain calldata and the calldata carries no signature, it falls back to deriving an `origin` from `message.from` **without any length check**:

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
``` [4](#0-3) 

`message.from` is a Solidity dynamic `bytes` field decoded from the raw ABI-encoded `body` of the delivered `PostRequest` [5](#0-4) , so nothing in the ABI decoding step constrains its length to 20 or 32 bytes — that constraint only exists as an implicit assumption about what the paired source-chain contract emits. If `from_bytes.len() < 20` and `source.is_evm()`, `from_bytes.len() - 20` underflows a `usize` subtraction (panics directly under overflow-checked arithmetic, or wraps to a huge value and then panics on the out-of-bounds slice index otherwise). If `source` is not EVM and `from_bytes.len() != 32`, `copy_from_slice` panics on the length mismatch. This is exactly the CVE-2017-17997 pattern: a length/shape assumption about attacker-influenced input is never validated before being used to index/build a fixed-size structure, and the code path panics instead of erroring.

### Impact Explanation
`on_accept` is invoked by `pallet-ismp`'s router when delivering a `PostRequest`, which is reached through the fully permissionless, unsigned `handle_unsigned` extrinsic [6](#0-5)  — any relayer can submit a proof for any request that was actually emitted on a registered source contract (`ContractToAsset` mapping) and get it executed for free. If that source contract (which could be a newly onboarded, buggy, or compromised token-bridge counterpart — the codebase itself acknowledges elsewhere that "the contract on chain could be compromised" [7](#0-6) ) ever emits a `from` value whose length is not exactly 20/32 bytes while also supplying non-empty, unsigned `data`, the runtime panics inside block execution. A WASM runtime trap during STF execution aborts block production for every node that tries to include this message, effectively halting further message delivery on that channel until governance intervenes — this satisfies the "route unable to deliver messages" impact criterion.

### Likelihood Explanation
Reachability requires only a relayed message with a relayed proof through the standard unsigned dispatch path; no privileged role is needed. The trigger condition (non-20/32-byte `from` with unsigned calldata) depends on the source-side contract's encoding discipline, which is not enforced on-chain by any ABI-level constraint — dynamic `bytes` accepts any length. This makes the vulnerability latent but directly reachable by an unprivileged relayer/token-bridger the moment any paired source contract (including future or non-reference integrations) fails to always emit exactly 20/32-byte `from` values.

### Recommendation
Apply the same explicit length validation used in `on_timeout` (lines 224-232) and for `message.to` (lines 63-71) to the `message.from` usage inside `on_accept`'s calldata-origin fallback (lines 177-186): return `HftError::InvalidSenderLength(from_bytes.len())` (or equivalent) for any length other than 20 (EVM) / 32 (non-EVM) instead of slicing/copying unchecked.

### Proof of Concept
1. Register a source contract/asset mapping via `ContractToAsset` for some `source` state machine (this is normal onboarding, not privileged from the relayer's perspective).
2. Have that source contract (or a compromised/nonstandard variant of it) emit a `PostRequest` whose ABI-encoded body decodes to a `Message` with `to` = 32 valid bytes, `data` = a `SubstrateCalldata` with `signature: None` and a runtime call, and `from` set to e.g. 5 bytes (any length not 20 for an EVM source, or not 32 for a substrate source).
3. A relayer submits a valid state proof for this request through `pallet_ismp::handle_unsigned`.
4. During execution, `Pallet::on_accept` reaches the `else` branch at line 177, computes `from_bytes.len() - 20` (or `copy_from_slice` with mismatched lengths), and panics, aborting block execution for every node processing this extrinsic.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L52-59)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L177-186)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L224-232)
```rust
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
					Err(HftError::InvalidSenderLength(from_bytes.len()))?
				}
```

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp_relayer.rs (L1194-1198)
```rust
		/// Defence-in-depth: an explicitly RLP-encoded zero address is
		/// rejected the same way an unset slot is, so a malicious
		/// actor can't claim a reward by writing zeros. (In practice
		/// the EVM would never emit this — leading zeros are stripped
		/// — but the contract on chain could be compromised.)
```
