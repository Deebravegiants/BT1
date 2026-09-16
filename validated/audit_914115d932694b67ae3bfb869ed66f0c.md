### Title
Unsigned cross-chain calldata dispatches a runtime call with the origin derived from the EVM sender address instead of the token beneficiary - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`pallet-hyper-fungible-token`'s `on_accept` lets an inbound token transfer carry optional embedded `SubstrateCalldata` that is dispatched as a runtime call. When the payload includes a `signature`, the origin is cryptographically bound to the `beneficiary` (the account that actually received the minted/transferred funds). When no signature is supplied, the pallet instead derives the dispatch origin directly from `message.from` — the raw sender field carried inside the attacker-controlled cross-chain message body — and dispatches the embedded `runtime_call` as that account, with no proof that the entity submitting the message controls that identity.

### Finding Description
In `modules/pallets/hyper-fungible-token/src/module.rs`, `on_accept` decodes an ABI `Message` from the `PostRequest` body [1](#0-0) . The optional `SubstrateCalldata` is decoded from `message.data`, and the pallet computes an `origin` to dispatch `substrate_data.runtime_call` under:

```rust
let origin = if let Some(signature) = substrate_data.signature {
    // ... signature verified against `beneficiary_bytes` ...
    beneficiary.clone()
} else {
    let from_bytes = message.from.as_ref();
    if source.is_evm() {
        T::EvmToSubstrate::convert(H160::from_slice(&from_bytes[from_bytes.len() - 20..]))
    } else {
        let mut account = [0u8; 32];
        account.copy_from_slice(from_bytes);
        account.into()
    }
};
``` [2](#0-1) 

`message.from` is a field of the ABI-encoded `Message` struct that the *sender contract on the source chain* controls arbitrarily when constructing the outbound transfer payload — it is not authenticated as belonging to the account submitting the calldata to be dispatched. The `_authenticate`-style check performed for this module only verifies that the *contract* address (`ContractToAsset::<T>::get(source, &from)`) is a registered token-bridge counterpart [3](#0-2) ; it says nothing about whose identity `message.from` (a payload field, not the request's `from`) claims to be. In the unsigned branch, that unauthenticated identity is used directly as `RawOrigin::Signed(origin)` to dispatch an arbitrary, filter-permitted `RuntimeCall`:

```rust
runtime_call.dispatch(RawOrigin::Signed(origin.clone()).into())
``` [4](#0-3) 

This is structurally the same class of bug as ALPINE-CVE-2019-13057: a component that legitimately handles one identity (the token beneficiary) is not properly isolated from being used to authorize actions "as" a *different* identity (an arbitrary `message.from` value) that the caller never actually proved control over. Any account able to reach the EVM-side token contract's `send` path (i.e., any unprivileged user who can call the paired EVM `HyperFungibleToken`/token-gateway contract, since there is no restriction on who can initiate a token transfer) can set `message.from` to any 20-byte or 32-byte value and embed a `SubstrateCalldata` with `signature = None`, causing Hyperbridge's `pallet-hyper-fungible-token` to dispatch an arbitrary permitted runtime call as that forged origin — including origins that were never party to the transfer and that the actual caller has no authorization over.

### Impact Explanation
Because `RawOrigin::Signed(origin)` reaches `Dispatchable::dispatch`, any pallet call not excluded by `BaseCallFilter` can be executed as an arbitrary chosen `AccountId` on Hyperbridge, filtered only by the runtime's `BaseCallFilter` — not by any real signature or account-ownership check. Depending on what calls the runtime's filter permits for signed origins (transfers, staking, asset operations, proxy calls, etc.), this allows theft or unauthorized manipulation of funds/state belonging to victim accounts whose raw account bytes an attacker guesses or targets (e.g., well-known treasury/pallet accounts, exchange deposit accounts, or any known public key), by forging `message.from` to match. This meets the "unauthorized app action" / "concrete theft" bar from a single unprivileged transfer.

### Likelihood Explanation
High reachability: any account can call the EVM token contract's outbound transfer function (registered as a valid `ContractToAsset` source) with an arbitrary `data` payload and an arbitrary `from` field in the encoded `Message`, without needing any elevated privilege, and without providing a signature. This directly triggers the vulnerable unsigned branch on delivery. The only friction is delivery by a relayer, which is a normal, unprivileged, permissionless part of the protocol.

### Recommendation
Do not derive a dispatch origin from `message.from` in the unsigned branch. Either:
1. Require a signature (as in the signed branch) to dispatch any runtime call, removing the unsigned fallback entirely; or
2. In the unsigned branch, restrict the origin strictly to `beneficiary` (the account that actually received the transferred funds and whose identity is already tied to the verified `to` field), rather than the attacker-supplied `message.from`.

### Proof of Concept
1. Attacker calls the paired EVM `HyperFungibleToken` contract's send/transfer function (or equivalent), registered on Hyperbridge via `ContractToAsset`, choosing:
   - `to` = attacker's own beneficiary account (to receive the minted/transferred tokens),
   - `data` = ABI-encoded `SubstrateCalldata { signature: None, runtime_call: <arbitrary permitted call, e.g. Balances::transfer_all(victim_targeted_as_signer)> }`,
   - the `Message.from` field forged to the raw bytes of a victim `AccountId` (e.g., a known treasury or exchange hot-wallet AccountId) instead of the attacker's real sender address.
2. A relayer delivers the `PostRequest` to Hyperbridge; `on_accept` runs, mints/transfers the token to `beneficiary` as normal, then hits the `data`-execution branch.
3. Since `substrate_data.signature` is `None`, `origin = T::EvmToSubstrate::convert(H160::from_slice(&from_bytes[..]))` (or the raw 32-byte conversion for substrate sources) is computed straight from the forged `Message.from`, with no proof of control.
4. `runtime_call.dispatch(RawOrigin::Signed(origin))` executes the embedded call as the forged victim account, bypassing `BaseCallFilter` only for disallowed calls, but succeeding for anything the filter permits (e.g., moving the victim's own funds if `Balances::transfer` isn't filtered for signed origins), all without the victim ever consenting or signing anything.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L54-56)
```rust
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-72)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L197-200)
```rust
			use sp_runtime::traits::Dispatchable;
			runtime_call
				.dispatch(RawOrigin::Signed(origin.clone()).into())
				.map_err(|e| HftError::CallDispatchError(e.error))?;
```
