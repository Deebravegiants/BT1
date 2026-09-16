## Analysis

Analogous to CVE‑2019‑8765 (memory corruption from processing malicious/untrusted content), the reachable Hyperbridge equivalent is a length-validation gap when parsing attacker‑controlled bytes from an incoming ISMP message, causing an unrecoverable panic in the runtime's message‑delivery path. Unlike the `to` field (validated for exactly 32 or 20 bytes), the `from` field of the decoded HFT `Message` is used with no length check before being sliced/copied.

### Title
Unvalidated length of attacker-controlled `message.from` causes panic (slice underflow / `copy_from_slice` length mismatch) in HFT `on_accept`, bricking message delivery - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`HyperFungibleToken::on_accept` decodes an ABI‑encoded `Message` from an untrusted ISMP `PostRequest.body` and validates the `to` field's length (must be 20 or 32 bytes), but performs no equivalent validation on the `from` field before using it in two panic‑prone operations.

### Finding Description
`on_accept` decodes the incoming cross-chain message body with `Message::abi_decode(&body)` [1](#0-0) . The `to` bytes are carefully length-checked before use [2](#0-1) , but when optional calldata carries no signature, the recovered `origin` is derived from `message.from` with no such guard:

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
``` [3](#0-2) 

- If `source.is_evm()` and `from_bytes.len() < 20`, `from_bytes.len() - 20` underflows `usize` — with overflow checks enabled (standard for Substrate runtimes) this panics immediately; without them it wraps to a huge index and the subsequent slice indexing panics on out-of-bounds access.
- In the non-EVM branch, `copy_from_slice` panics unless `from_bytes.len() == 32` exactly — any other length (including empty or 20-byte EVM-style addresses coming from an EVM source misclassified, or simply a caller who sets `from` to an arbitrary length) triggers a panic.

`message.from` is attacker-controlled: it is an arbitrary-length byte field inside the ABI‑encoded `Message` struct constructed by whoever calls the source bridge contract to originate the cross-chain transfer; the only authentication performed is that `source`/`from` (as the *contract* address, via `ContractToAsset::get(source, &from)` at the top of `on_accept`) maps to a registered asset — the `from`-as-bytes-length used later in the calldata path is not the same value checked there and is not re-validated at all before slicing.

### Impact Explanation
`on_accept` executes as part of the ISMP message handling / dispatch flow that is invoked for every relayed cross-chain message destined for the HFT module. A crafted message with calldata (`message.data` non-empty, `SubstrateCalldata.signature == None`) and a `from` field of any length other than 32 (or, for EVM sources, shorter than 20) deterministically panics during processing. Because panics in `no_std` runtime code abort execution rather than returning a `Result`, this is not a graceful application-level rejection: it aborts the enclosing extrinsic/block execution path handling the message, which breaks the HFT message-delivery route (a message that can never be successfully processed, and which can also be used to make block import/validation fail for any block that includes it) — matching the "route unable to deliver messages" impact category.

### Likelihood Explanation
Reaching this path only requires an unprivileged user to initiate an ERC20-token bridging transaction through the registered source contract with a crafted `data` field containing unsigned `SubstrateCalldata` and a `from` value whose byte length is not 32/not ≥20 as expected — no special privilege, governance, or relayer trust is needed, only that the message subsequently gets relayed and processed by `on_accept`, which is the normal path for every incoming HFT transfer with calldata.

### Recommendation
Validate `from_bytes.len()` explicitly before use, mirroring the `to_bytes` length check earlier in the function (accept exactly 20 or 32 bytes, left/right-pad as appropriate) and return `HftError::InvalidRecipientLength`/an equivalent typed error instead of panicking, for both the EVM slicing branch and the 32-byte `copy_from_slice` branch.

### Proof of Concept
1. Register a source contract/asset mapping normally via `ContractToAsset`.
2. From an EVM source, submit a bridging transaction whose ABI-encoded `Message.data` decodes to a `SubstrateCalldata` with `signature: None` and any `runtime_call`, while setting `Message.from` to fewer than 20 bytes (e.g., 0 bytes) when `source.is_evm()`, or to a length other than 32 bytes when `source` is not EVM.
3. Relay this request; `on_accept` reaches `&from_bytes[from_bytes.len() - 20..]` (or `account.copy_from_slice(from_bytes)`), causing an arithmetic underflow / length-mismatch panic instead of returning a decode error like the sibling `to`-field validation does. [4](#0-3) [5](#0-4)

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-187)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

			let origin = if let Some(signature) = substrate_data.signature {
				let multi_signature = MultiSignature::decode(&mut &*signature)
					.map_err(HftError::SignatureDecodeError)?;

				let nonce = frame_system::Pallet::<T>::account_nonce(beneficiary.clone());

				match multi_signature {
					MultiSignature::Ed25519(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let msg = sp_io::hashing::keccak_256(&payload);
						let pub_key = beneficiary_bytes
							.as_slice()
							.try_into()
							.map_err(|_| HftError::SignatureVerificationFailed)?;
						if !sp_io::crypto::ed25519_verify(&sig, msg.as_ref(), &pub_key) {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
					MultiSignature::Sr25519(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let msg = sp_io::hashing::keccak_256(&payload);
						let pub_key = beneficiary_bytes
							.as_slice()
							.try_into()
							.map_err(|_| HftError::SignatureVerificationFailed)?;
						if !sp_io::crypto::sr25519_verify(&sig, msg.as_ref(), &pub_key) {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
					MultiSignature::Ecdsa(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let preimage = vec![
							format!("{ETHEREUM_MESSAGE_PREFIX}{}", payload.len())
								.as_bytes()
								.to_vec(),
							payload,
						]
						.concat();
						let msg = sp_io::hashing::keccak_256(&preimage);
						let pub_key = sp_io::crypto::secp256k1_ecdsa_recover(&sig.0, &msg)
							.map_err(|_| HftError::EcdsaRecoveryFailed)?;
						let eth_address =
							H160::from_slice(&sp_io::hashing::keccak_256(&pub_key[..])[12..]);
						let substrate_account = T::EvmToSubstrate::convert(eth_address);
						if substrate_account != beneficiary {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
					MultiSignature::Eth(_) => Err(HftError::EthSignatureUnsupported)?,
				};

				beneficiary.clone()
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
