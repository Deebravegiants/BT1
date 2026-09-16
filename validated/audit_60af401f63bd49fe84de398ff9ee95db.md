### Title
Unsigned cross-chain calldata lets an attacker dispatch an arbitrary `RuntimeCall` as any spoofed account, gated only by `BaseCallFilter` - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
The jackson-databind CVE is a case of an unauthenticated payload being deserialized into an arbitrary/attacker-chosen type and then acted upon, with only a denylist (rather than a proof of legitimacy) standing between the attacker and code execution. The closest reachable analog in this codebase is `pallets/hyper-fungible-token`'s `on_accept` handler, which decodes attacker-supplied calldata embedded in a cross-chain `PostRequest.body` into a `T::RuntimeCall` and dispatches it, with the acting origin chosen from unauthenticated, attacker-controlled bytes when no signature is supplied, and the only safeguard being a `BaseCallFilter` denylist check.

### Finding Description
`Pallet::on_accept` in [1](#0-0)  decodes an ABI-encoded `Message` from the `PostRequest.body`, which is fully controlled by whatever caller invokes the corresponding dispatch function on the source-chain contract — the pallet only authenticates the `(source, from)` contract pair via `ContractToAsset`, not the contents of `message.from`/`message.data`.

If `message.data` is non-empty, it is decoded as `SubstrateCalldata` and, crucially, the identity used to dispatch the embedded call is derived differently depending on whether a `signature` field is present: [2](#0-1) 

When a signature *is* present, the signer is cryptographically verified against `substrate_data.runtime_call` and bound to the `beneficiary` account: [3](#0-2) 

But when **no signature is supplied**, the origin used to dispatch the call is derived directly from `message.from` — a field inside the attacker-supplied ABI body, not the ISMP-verified request sender: [4](#0-3) 

The decoded `runtime_call` is then dispatched as that spoofed origin, gated only by `BaseCallFilter::contains`, mirroring a denylist/blocklist gate rather than a positive authorization check: [5](#0-4) 

This is structurally analogous to the Jackson bug class: an attacker-controlled payload is deserialized into an arbitrary executable type (`T::RuntimeCall`) and then acted on using an attacker-chosen identity, with only a denylist (`BaseCallFilter`) — which is typically tuned to block obviously dangerous calls, not to enumerate every dispatchable safely reachable from an arbitrary spoofed `AccountId` — standing in the way of unauthorized action. Any dispatchable not explicitly filtered can be executed as an arbitrary chosen account (any 20- or 32-byte value the attacker picks), which is a privilege/identity-spoofing primitive reachable from a single unprivileged cross-chain post request.

### Impact Explanation
An attacker who can call the source-chain `HyperFungibleToken` contract (or equivalent bridging entrypoint) with a crafted `Message.data` payload and no signature can cause the destination pallet to dispatch an arbitrary runtime call as any account they choose (e.g., a governance account, an exchange's hot-wallet-controlled account, or a treasury account), as long as that call type isn't on the `BaseCallFilter` denylist. This can result in unauthorized asset transfers, unauthorized approvals, or unauthorized application actions taken "as" a victim account — i.e., theft of funds or unauthorized app action from a completely unprivileged, permissionless cross-chain message.

### Likelihood Explanation
Reachable from a single unprivileged token-bridge transfer: any account that can call the token bridge's transfer entrypoint on the source chain can embed arbitrary `SubstrateCalldata` (with no signature) in the transfer payload, and the destination pallet's `on_accept` will execute it as the spoofed `from` identity. The only barrier is whatever the runtime's `BaseCallFilter` denies, which is generally maintained as a safety denylist against obviously catastrophic calls, not against every call reachable by an attacker with a spoofed identity — matching the "blocklist bypass" pattern from the report.

### Recommendation
Do not derive the dispatch origin from unauthenticated bytes inside the message body. Require a valid signature (as already implemented in the `Some(signature)` branch) for *every* call that carries executable calldata, or otherwise strongly restrict what `message.from`-derived origins are permitted to do (e.g., disallow dispatch entirely when unsigned, or scope the resulting origin to a pallet-controlled sub-account rather than an arbitrary externally chosen `AccountId`).

### Proof of Concept
1. On the source EVM chain, call the bridge/app contract path that populates `HyperFungibleToken.Message` with an attacker-chosen `from` (e.g., set to the 32-byte representation of a victim/governance `AccountId`), a minimal valid `to`/`amount`, and `data` = ABI-encoded `SubstrateCalldata { signature: None, runtime_call: <encoded RuntimeCall not covered by BaseCallFilter> }`.
2. Relay the resulting cross-chain `PostRequest` to the destination chain running `pallet-hyper-fungible-token`.
3. `on_accept` decodes the message, hits the `else` branch (no signature) at `modules/pallets/hyper-fungible-token/src/module.rs:176-187`, converts `message.from` directly into the dispatch origin, and calls `runtime_call.dispatch(RawOrigin::Signed(origin))` at lines 189-200 — executing the attacker's chosen call as the spoofed account.

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-126)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

			let origin = if let Some(signature) = substrate_data.signature {
				let multi_signature = MultiSignature::decode(&mut &*signature)
					.map_err(HftError::SignatureDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L130-173)
```rust
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L175-187)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-203)
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

			frame_system::Pallet::<T>::inc_account_nonce(origin);
		}
```
