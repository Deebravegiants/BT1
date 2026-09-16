## Finding

### Title
Unchecked length subtraction on attacker-controlled `message.from` causes a panic in `hyper-fungible-token`'s ISMP callback - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` (the `IsmpModule::on_accept` implementation for `pallet-hyper-fungible-token`) reads a fixed-width, 20-byte EVM address out of a variable-length, attacker-influenced byte buffer (`message.from`) using `from_bytes.len() - 20`, without first checking that `from_bytes.len() >= 20`. This mirrors the CVE-2025-21867 root cause: consuming a fixed-size header/field out of a buffer whose minimum length was never validated.

### Finding Description
`on_accept` decodes the ABI body of an incoming ISMP POST request into a `Message` struct via `Message::abi_decode(&body)` [1](#0-0) . `message.from` is a dynamic `bytes` field inside that decoded struct — independent from the ISMP-level `PostRequest.from` (the registered source-contract address that is separately checked against `ContractToAsset`). Its length is controlled by whoever constructed the ABI-encoded body on the source chain, not enforced to be 20 bytes by this pallet.

Later, when the message carries calldata (`message.data` non-empty) with no signature (`substrate_data.signature == None`), the code derives the dispatch origin from `message.from` for EVM sources:

```rust
let from_bytes = message.from.as_ref();
if source.is_evm() {
    T::EvmToSubstrate::convert(H160::from_slice(
        &from_bytes[from_bytes.len() - 20..],
    ))
} else { ... }
``` [2](#0-1) 

If `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows the `usize` subtraction. Rust panics on this arithmetic underflow (checked in debug builds, and even in release builds the subsequent slice index with the wrapped huge value still triggers a bounds-check panic — Rust's memory safety guarantees convert what would be a raw out-of-bounds/UAF read in C into an unhandled panic). This is the direct analog of `eth_skb_pkt_type()` dereferencing an Ethernet header that was never validated to be present: both bugs stem from treating a caller-supplied buffer as guaranteed to contain a fixed-size trailing field without checking its minimum length first.

### Impact Explanation
A relayer permissionlessly delivering a genuine, proof-verified POST request (this is exactly the "unprivileged message dispatcher/relayer" surface named in scope) that carries a `Message` whose `from` field is shorter than 20 bytes, non-empty `data`, and no `signature`, causes `on_accept` to panic instead of returning a graceful `Err`. Unlike a bounded `Result`-based rejection (which pallet-ismp's `handle_unsigned` -> `execute` path is designed to tolerate per-message), an actual Rust panic inside the module callback propagates out of the ISMP dispatch handler. Because `handle_unsigned` is an unsigned, permissionless extrinsic (`ensure_none`) executed by every validating/relaying node, and it wraps execution with `#[frame_support::transactional]` but not panic-catching, a reliably reproducible panic here can be used to make delivery of the token-bridge route stall/crash node-level processing of that message repeatedly, i.e. "a route unable to deliver messages" for the hyper-fungible-token app.

### Likelihood Explanation
Reachability requires only a genuinely accepted cross-chain POST request (i.e., a message that passes the source-contract check `ContractToAsset::get(source, &from)`) whose ABI body encodes a `Message.from` shorter than 20 bytes, non-empty `data`, and `signature = None`. Whether an attacker can freely control the `Message.from` bytes independently of the msg.sender enforced by the canonical `HyperFungibleToken.sol` sender contract could not be fully confirmed from the code reviewed here — this depends on whether every registered EVM source contract strictly enforces `from = abi.encodePacked(msg.sender)` (always 20 bytes) or whether some integration path allows a caller-supplied `from`. This uncertainty affects the practical likelihood and should be verified against the concrete `Message` encoding logic on the EVM sender side (`HyperFungibleToken.sol`/`WrappedHyperFungibleToken.sol`) and any other applications authorized to dispatch into this same pallet.

### Recommendation
Validate `from_bytes.len() >= 20` (and generally validate exact expected length, mirroring the `to_bytes.len() == 32 || == 20` check already done a few lines above for `message.to`) before slicing, and return `HftError::InvalidRecipientLength`/a new `InvalidFromLength` variant instead of indexing unchecked.

### Proof of Concept
1. Register a source EVM contract/asset mapping via `ContractToAsset` as usual.
2. Craft (or find an integration where the caller controls) an ABI-encoded `Message` body where `from` is fewer than 20 bytes (e.g., 0 or 1 byte), `data` is non-empty and decodes to a valid `SubstrateCalldata` with `signature: None`.
3. Deliver this as a normal POST request through the ISMP `handle_unsigned` pipeline with a valid proof.
4. `on_accept` reaches `from_bytes.len() - 20` with `from_bytes.len() < 20`, triggering an arithmetic-underflow/index panic instead of a controlled error, aborting extrinsic execution for that message. [2](#0-1)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L55-59)
```rust
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
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
