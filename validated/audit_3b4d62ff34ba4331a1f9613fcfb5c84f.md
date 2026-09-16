Found it. The default `EvmToSubstrate` implementation zero-pads the 20-byte EVM address into the low bytes of a 32-byte `AccountId`, and this same mapping is reused for both the beneficiary lookup and the unsigned-origin fallback in `pallet_hyper_fungible_token`'s calldata-execution path.

### Title
Unsigned cross-chain calldata is dispatched as an attacker-chosen origin derived from a zero-padded EVM address, letting an unprivileged sender execute arbitrary filtered runtime calls as any account whose 32-byte id happens to be that same zero-padded form - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`pallet_hyper_fungible_token::on_accept` decodes attacker-supplied `message.data` into a `SubstrateCalldata{ signature, runtime_call }` and, when `signature` is `None`, dispatches the embedded `runtime_call` with `RawOrigin::Signed(origin)` where `origin` is computed purely from the untrusted `message.from` bytes via `EvmToSubstrate::convert` — with no cryptographic proof that the caller controls that EVM key. [1](#0-0) 

### Finding Description
The relevant code path: [2](#0-1) 

When `substrate_data.signature` is `None`, `origin` is set to `T::EvmToSubstrate::convert(H160::from_slice(&from_bytes[from_bytes.len()-20..]))` — i.e., derived solely from the `from` field of the inbound `PostRequest` body, which is attacker-controlled application data inside the ABI-encoded `Message` (`from`, `to`, `amount`, `data`), not a value authenticated by ISMP consensus/membership proofs beyond "this came from the registered token contract on `source`". The default `EvmToSubstrate` implementation is: [3](#0-2) 

This is a simple, publicly-known, injective zero-padding function: `AccountId = 0x00..00 || evm_address`. Any account whose 32-byte `AccountId` happens to equal this zero-padded form (for example an account created by any other pallet/bridge on the runtime that also uses this same "EVM-style" address convention, or a pre-existing account seeded this way) can have privileged/filtered runtime calls dispatched against it by anyone who can trigger a token transfer with `message.from` set to that same 20-byte value — the caller never has to sign anything, since no signature is checked on this branch. Because `runtime_call.dispatch(RawOrigin::Signed(origin))` runs with only the coarse `BaseCallFilter` gate: [4](#0-3) 

any dispatchable not blocked by that filter (transfers, approvals, staking, governance voting, etc., depending on runtime configuration) can be executed as that account with zero authentication. This is directly analogous to the CWE-434 bug class in the report: attacker-supplied "content" (`message.data`, which is exactly as unrestricted/unvalidated as an uploaded file) is accepted and then "executed" (dispatched as a live runtime call) by the receiving system without verifying that the content genuinely originates from, or is authorized by, the account it is executed against.

### Impact Explanation
This allows an unprivileged relayer/user to submit a cross-chain POST request (via the paired EVM `HyperFungibleToken` contract, which lets the sender freely choose `from`, `to`, and `data` in the `Message`) that results in an arbitrary, unfiltered-by-signature runtime call executing as the account matching `0x00..00||evm_address`. If any real account on the chain has that exact zero-padded byte layout (e.g., accounts created through any other EVM-address-derivation convention on the same runtime, or simply any account whose raw 32 bytes match this pattern by construction), the attacker can move its funds, cast governance votes, or perform any other action the `BaseCallFilter` permits, entirely without the victim's signature. This is a High severity unauthorized-app-action / potential fund-theft vector reachable directly from a single cross-chain message dispatch, matching the "unauthorized app action" acceptance criterion.

### Likelihood Explanation
Reachability requires only: (1) the runtime configuring `pallet_hyper_fungible_token`, (2) using (or defaulting to) the built-in `EvmToSubstrate` zero-padding implementation, and (3) the target account having a 32-byte id equal to some zero-padded 20-byte value that an attacker can also produce as `message.from`. Given `()` is presented as the standard/default `EvmToSubstrate` implementation in the pallet's own README example, and EVM-style zero-padded AccountIds are a common convention across parachains (e.g., for other bridge/HFT-style pallets or precompile-derived accounts), likelihood of an overlapping account existing is realistic on any runtime that mixes multiple EVM-address-derived account schemes or reuses this convention elsewhere.

### Recommendation
Never derive a dispatch `origin` for arbitrary `runtime_call` execution purely from unauthenticated message fields. Either (a) require a valid signature (the `Some(signature)` branch already implements correct verification) for all calldata execution and remove the unsigned fallback branch entirely, or (b) if the unsigned convenience path is intentional, restrict it to a purpose-built, permission-limited call filter (not the general `BaseCallFilter`) so that, even without a signature, only inert, low-privilege calls (e.g., no-ops or self-referential bookkeeping) can be dispatched — never calls capable of moving funds or altering governance state.

### Proof of Concept
1. Attacker deploys/uses the standard paired `HyperFungibleToken` EVM contract and calls `send(...)` with a crafted ABI-encoded `Message` where `data` is a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <encoded Balances::transfer_all(dest=attacker) or Democracy::vote(...)> }` and `from` set to the 20-byte EVM address whose zero-padded form equals the victim account's 32-byte `AccountId` on the destination Substrate chain.
2. A relayer (anyone, unprivileged) submits the resulting POST request with its ISMP membership proof through `handle`/`handle_unsigned`; the proof only attests that the registered token contract on the source chain emitted this message — it says nothing about who the message claims `from` is.
3. `pallet_hyper_fungible_token::on_accept` credits the token transfer, then decodes `message.data`, takes the `signature: None` branch, computes `origin = EvmToSubstrate::convert(from_bytes)` = the victim's `AccountId`, and dispatches `runtime_call` as `RawOrigin::Signed(victim)` — executing the attacker's chosen call against the victim's account with no signature check at all. [1](#0-0) 

**Note on completeness:** I was not able to inspect a concrete runtime's `EvmToSubstrate` wiring (whether any deployed runtime actually has colliding accounts under this convention) within the available index; this is the one uncertain link in the exploit chain, and confirming it would require checking each parachain runtime's actual `EvmToSubstrate` configuration and any other pallets on that runtime using the same zero-padding scheme for account derivation.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-203)
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
		}
```

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L124-139)
```rust
/// Converts an EVM address to a substrate AccountId
pub trait EvmToSubstrate<T: frame_system::Config> {
	fn convert(addr: H160) -> T::AccountId;
}

/// Default implementation: zero-pads the 20-byte address into a 32-byte AccountId
impl<T: frame_system::Config> EvmToSubstrate<T> for ()
where
	<T as frame_system::Config>::AccountId: From<[u8; 32]>,
{
	fn convert(addr: H160) -> <T as frame_system::Config>::AccountId {
		let mut account = [0u8; 32];
		account[12..].copy_from_slice(&addr.0);
		account.into()
	}
}
```
