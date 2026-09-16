Confirmed: on the Solidity side, `message.from` is always set to `abi.encodePacked(msg.sender)` by the sending contract itself [1](#0-0) , so an attacker cannot forge an arbitrary `from` field through the normal `send()` path. However, the pallet's unsigned-calldata branch trusts that field completely to derive the dispatch origin, with no cryptographic binding to the actual caller beyond what the EVM contract chooses to encode.

### Title
Unsigned cross-chain calldata in `pallet-hyper-fungible-token` dispatches arbitrary runtime calls under attacker-influenced origin - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` decodes an ABI `Message` from an ISMP `PostRequest` body and, when `message.data` is non-empty, decodes a `SubstrateCalldata` containing a `runtime_call` and an optional `signature`. When `signature` is `None`, the origin used to dispatch the call is derived directly from `message.from` — attacker/source-contract-supplied bytes — with no signature check at all, only a `BaseCallFilter` check [2](#0-1) .

### Finding Description
`on_accept` computes `origin` from `message.from` in the unsigned branch by directly slicing/copying the bytes into an `AccountId` (20-byte EVM addresses are converted via `T::EvmToSubstrate::convert`, 32-byte values are copied straight into a `[u8;32]`) [3](#0-2) . It then decodes `substrate_data.runtime_call` into `T::RuntimeCall` and dispatches it as `RawOrigin::Signed(origin)` [4](#0-3) , with the only gate being `BaseCallFilter::contains`, which filters dispatchable *categories* (e.g. maintenance-mode blocks) but performs no per-account authorization.

The security of this path rests entirely on the destination pallet's trust that `message.from` equals the actual originating `msg.sender` on the source chain. That invariant holds for the reference `HyperFungibleToken.sol`/`HyperFungibleTokenUpgradeable.sol`/`WrappedHyperFungibleToken*.sol` contracts, which hardcode `from: abi.encodePacked(msg.sender)` [1](#0-0) . But `on_accept` authenticates only that the ISMP request's `from`/`source` matches a registered peer contract via `ContractToAsset::<T>::get(source, &from)` [5](#0-4)  — it does not, and structurally cannot, verify that the peer contract itself enforced `from == msg.sender` for every message it emits. Any peer deployment that is a fork, an upgrade, or a different implementation of the HFT wire format (including the upgradeable/wrapped variants, or any third-party contract a governance/owner action registers as a peer) could emit an arbitrary `from` value, letting an unprivileged EVM caller impersonate any Substrate `AccountId` and dispatch arbitrary filtered-but-otherwise-unrestricted runtime calls as that account — a forged-message/unauthorized-app-action bug class analogous to the GraphQL advisory's "attacker-controlled input drives execution of an unintended, powerful operation," here manifesting as unsigned cross-chain calldata driving privileged `Dispatchable::dispatch` under an attacker-chosen origin.

### Impact Explanation
If reached (i.e., against a peer whose `from` value is not strictly `msg.sender`, or via any future/alternate registered peer implementation), this allows impersonation of arbitrary Substrate accounts to execute any dispatchable not blocked by `BaseCallFilter` — including transfers, governance votes, or other privileged extrinsics — as that account, which is unauthorized app action and potential theft of funds held by the impersonated account.

### Likelihood Explanation
Low-to-medium given the current reference contracts hardcode `from: abi.encodePacked(msg.sender)`, so exploitation requires a differently-behaved registered peer contract (e.g. malicious/buggy upgrade, custom integrator implementation registered via `ContractToAsset`/chain-config, or a future contract version) rather than a flaw reachable purely through the standard EVM contracts audited here. It is not exploitable through the documented `send()` flow alone.

### Recommendation
Do not trust `message.from` as an authorization source for unsigned calldata dispatch. Either require a signature on all calldata-carrying messages (remove the unsigned branch), or restrict the unsigned-calldata dispatch to only ever use `beneficiary` (the token recipient, already validated) rather than a value derived from attacker-influenced `message.from`, and/or scope `BaseCallFilter` plus an explicit allow-list for calls reachable via bridged calldata.

### Proof of Concept
1. Governance/owner registers a peer EVM contract for some chain via `ContractToAsset`/config that (unlike the reference `HyperFungibleToken.sol`) allows the caller to set an arbitrary `from` field in its emitted `Message` (or a future/forked contract version does this).
2. Attacker calls that contract, setting `from` = victim's Substrate account bytes and `data` = ABI-encoded `SubstrateCalldata { signature: None, runtime_call: <victim-draining call> }`.
3. On relay, `Pallet::on_accept` derives `origin = victim_account` from `message.from` with no signature check [6](#0-5)  and dispatches `runtime_call` as the victim, subject only to `BaseCallFilter`.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L241-246)
```text
        bytes memory body = abi.encode(Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L54-56)
```rust
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-200)
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
```
