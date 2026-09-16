### Title
Unsigned calldata path lets any cross-chain sender dispatch arbitrary runtime calls as the message's derived beneficiary account - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`Pallet::on_accept` in the `hyper-fungible-token` module decodes an ISMP `PostRequest` body into a `Message`, and when `message.data` is non-empty it decodes a `SubstrateCalldata { signature: Option<Vec<u8>>, runtime_call: Vec<u8> }` and dispatches `runtime_call` on-chain. If `substrate_data.signature` is `None`, no cryptographic signature is checked at all — the dispatch origin is simply derived from `message.from` (the raw cross-chain sender bytes reported in the bridged message body), and the decoded `RuntimeCall` is dispatched as `RawOrigin::Signed(origin)` with only a `BaseCallFilter` check. [1](#0-0) 

### Finding Description
The `data` field of the bridged `Message` (a raw ABI `bytes` field controlled by whoever calls `send`/dispatches the token-bridge message on the source chain, or is otherwise reachable via any counterparty contract mapped via `ContractToAsset`) is decoded into `SubstrateCalldata`. This struct carries an *optional* signature: [2](#0-1) 

When the signature is omitted, the code takes the "unsigned" branch and derives the dispatch origin purely from `message.from` — which is attacker-supplied data embedded in the message body being relayed, not an authenticated Substrate signature: [3](#0-2) 

The decoded `RuntimeCall` is then dispatched with `RawOrigin::Signed(origin)`, gated only by the runtime's `BaseCallFilter`: [4](#0-3) 

This mirrors the CVE-2017-1001002 bug class conceptually: attacker-controlled payload data embedded in a message is interpreted and *executed* as code (here, a SCALE-encoded runtime call) under a derived, non-cryptographically-verified authority, rather than requiring proof of possession of the target account's signing key for every dispatch path. The `from` field is set by whatever counterparty contract/module sent the cross-chain message; since `on_accept` only authenticates the *source contract* (via `ContractToAsset`) and not the semantic content of `message.from`/`message.to`, a message can carry a `from`/`to` value that maps to *any* AccountId on the destination chain, and immediately dispatch a runtime call "as" that account whenever the unsigned branch is used.

### Impact Explanation
An attacker who can get an ISMP `PostRequest` routed to this module from a contract registered in `ContractToAsset` (i.e., any properly configured bridged token contract on the source chain, which the attacker fully controls if they deploy/operate on an EVM chain and register/whitelist it, or otherwise supply a `from`/`to` value of their choosing in the message they send) can set `message.from` to an arbitrary 20 or 32-byte value and attach `SubstrateCalldata { signature: None, runtime_call: <arbitrary allowed call> }`. This dispatches the call as `RawOrigin::Signed(<attacker-chosen account>)`, letting the attacker perform actions (e.g., asset transfers, governance-permitted calls not blocked by `BaseCallFilter`) as any account whose derived AccountId they can compute from `message.from`, without ever proving control of that account's private key. This is unauthorized app action / potential fund theft depending on which dispatchables the `BaseCallFilter` permits.

### Likelihood Explanation
This path is reached automatically on every successful token transfer/mint that carries non-empty calldata via the standard cross-chain message flow (`on_accept`), requiring no relayer privilege beyond delivering a valid ISMP proof for a message originating from a contract already registered in `ContractToAsset`. Because signature verification is optional (`Option<Vec<u8>>`) rather than mandatory, exploitation only requires omitting the signature field, which is the "normal", cheaper code path.

### Recommendation
Require a valid signature for every dispatched `runtime_call`, or otherwise strongly cryptographically bind the derived origin to a beneficiary the message truly proves control over (e.g., only allow the unsigned path when `origin == beneficiary` derived purely from the token-mint recipient, and make it a *no-privilege* origin such as `RawOrigin::None` with an explicit filtered allow-list, rather than `RawOrigin::Signed`). At minimum, treat the unsigned branch as untrusted and disallow dispatching state-mutating/asset-moving calls under it.

### Proof of Concept
1. Register/operate a source-chain contract that is mapped in `ContractToAsset` for some `local_asset_id`.
2. Craft an ISMP `PostRequest` body that ABI-decodes to `Message { from: <victim_account_bytes>, to: <attacker_or_any>, amount: 0-or-more, data: SCALE(SubstrateCalldata{ signature: None, runtime_call: SCALE(<Transfer call moving victim's assets>) }) }`.
3. Deliver this message (with a valid ISMP membership proof for the registered source contract) to the destination chain.
4. `on_accept` runs: mint/transfer to beneficiary occurs, then the unsigned calldata branch derives `origin` from `message.from` (== victim account) and dispatches the attacker-chosen `runtime_call` as `RawOrigin::Signed(victim_account)`, executing the call with the victim's authority without any signature check.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-202)
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

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L105-113)
```rust
/// SCALE-encoded calldata for executing a runtime call on the destination substrate chain
#[derive(Debug, Clone, Encode, Decode, scale_info::TypeInfo, PartialEq, Eq)]
pub struct SubstrateCalldata {
	/// Optional SCALE-encoded [MultiSignature](sp_runtime::MultiSignature) of the beneficiary's
	/// account nonce and the encoded runtime call
	pub signature: Option<Vec<u8>>,
	/// SCALE-encoded runtime call to execute
	pub runtime_call: Vec<u8>,
}
```
