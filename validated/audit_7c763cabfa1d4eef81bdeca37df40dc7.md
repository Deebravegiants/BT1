### Title
Unsigned cross-chain calldata path dispatches an arbitrary `RuntimeCall` using an unauthenticated `message.from` as origin - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`Pallet::on_accept` in the hyper-fungible-token pallet decodes optional calldata carried inside a cross-chain token-transfer message and, when no signature is attached, derives the dispatch `origin` directly from an attacker-influenced field of the ABI-decoded message body (`message.from`) rather than from any cryptographically verified identity, then dispatches an arbitrary `T::RuntimeCall` as that origin.

### Finding Description
`on_accept` first authenticates only the *source contract* via `ContractToAsset::<T>::get(source, &from)` — where `from` here is the ISMP `PostRequest.from` (the registered gateway contract address on the source chain) [1](#0-0) . It then ABI-decodes the request `body` into a `Message` struct that itself carries an independent `from` field, plus `to`, `amount`, and optional `data` [2](#0-1) . This inner `message.from` is payload content chosen by whoever calls the source-chain gateway contract — it is not the same as the checked `PostRequest.from`, and nothing in this pallet verifies it against any signature by default.

When `message.data` is non-empty it is decoded into `SubstrateCalldata { signature: Option<...>, runtime_call }`. Two branches decide the dispatch `origin`:

- If `signature` is `Some(..)`, the code performs a real cryptographic check: it hashes `(nonce, runtime_call)` and verifies an Ed25519/Sr25519/Ecdsa signature against the beneficiary's derived key/address before using `beneficiary` as the origin [3](#0-2) .
- If `signature` is `None`, the origin is instead derived *without any authentication* straight from `message.from`, converted to a Substrate `AccountId` (via `EvmToSubstrate` for EVM sources or a raw 32-byte copy for substrate sources) [4](#0-3) .

The decoded `runtime_call` is only checked against `BaseCallFilter::contains` (a maintenance/allow-list filter, not an authorization check) and is then dispatched with `RawOrigin::Signed(origin)` [5](#0-4) .

This is structurally the same bug class as the Keras `Lambda` deserialization advisory: a security-relevant guard (here, "is this dispatch cryptographically authorized by the origin account") is only enforced on one branch of an `Option`, and the `None` branch is silently treated as "trust the caller-supplied identity" instead of "deny/require proof." In Keras, `safe_mode=None` was conflated with `False` (disabled) instead of the intended default-deny; here, "no signature provided" is conflated with "the wire-supplied `from` field is a legitimate signer" instead of failing closed (e.g., requiring a signature whenever `data` triggers a call dispatch, or restricting the unsigned path to non-privileged/no-call situations). The result in both cases is that untrusted, attacker-shaped input is deserialized into an executable action and executed with elevated trust.

### Impact Explanation
Because the gateway/transfer path is permissionless (any account can call the registered source-chain contract to initiate a bridged transfer and choose the `message.from`/`message.data` payload), a caller who can make `message.from` resolve to an arbitrary account (or to an account they do not control, e.g. a protocol/treasury account, a governance-controlled account, or another user's derived account) can get Hyperbridge's runtime to execute a `RuntimeCall` — subject only to the base call filter, not to any real permission check — as `RawOrigin::Signed(that account)`. Depending on which calls the base filter allows through, this can be used to perform unauthorized app actions (e.g., asset transfers, approvals, governance-adjacent calls) as an account the actual message sender never proved control of. This satisfies the "unauthorized app action" bar in the validation criteria, reachable from a single relayed cross-chain message/token transfer.

### Likelihood Explanation
The path is reachable by any account able to call the registered HFT gateway contract on a source chain and craft `message.data` (`SubstrateCalldata` with `signature: None` and an arbitrary SCALE-encoded `runtime_call`) — no relayer privilege, no admin action, and no private key for the impersonated account is required on the Hyperbridge side. The only gate on the destination is `BaseCallFilter::contains`, which is a coarse maintenance-mode filter and not designed as a per-call authorization mechanism. The actual exploitability hinges on whether the EVM/Substrate-side gateway contract binds `message.from` to the true caller (`msg.sender`) for every call path; that contract's enforcement was not available for direct inspection in this pass (index limits), so this should be confirmed against the live gateway contract source before treating this as fully proven, but the pallet-side logic itself provides no independent guarantee and fails closed only when a signature happens to be supplied.

### Recommendation
Require a valid signature (bound to `message.from`/the derived account and to the specific `runtime_call` + nonce) on every path that leads to a `RuntimeCall` dispatch, i.e., remove the unsigned/`None` branch's ability to select an arbitrary dispatch origin, or restrict the unsigned branch to a `None`-origin/no-dispatch case entirely. At minimum, treat `signature: None` as "deny privileged dispatch" (fail closed) rather than "derive origin from unauthenticated wire data," mirroring the fix pattern for the Keras issue (never conflate "unset" with "disabled/bypassed").

### Proof of Concept
1. Register (or use an already-registered) HFT gateway contract/asset mapping for a source chain, per `ContractToAsset`.
2. From that source chain, call the gateway's transfer function such that the resulting ISMP `PostRequest.from` is the registered gateway contract (passes the `ContractToAsset` check), while the ABI-encoded `Message.from` field is set to bytes representing a *victim* account (any account whose funds/permissions are desired), and `Message.data` is set to `SubstrateCalldata { signature: None, runtime_call: <encoded privileged call> }`.
3. Relay the resulting `PostRequest` to Hyperbridge. `on_accept` runs, mints/transfers the bridged amount to the `beneficiary` (`message.to`), then — because `signature` is `None` — computes `origin` from `message.from` (the victim's bytes) without any proof of authorization, and dispatches `runtime_call` as `RawOrigin::Signed(victim)`.
4. Any call not excluded by `BaseCallFilter` executes as the victim account, confirming that dispatch happened without the victim ever signing anything.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-56)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-59)
```rust
		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L124-173)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-202)
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
```
