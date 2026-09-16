### Title
Signature-less calldata execution in `pallet-hyper-fungible-token::on_accept` lets any EVM/Substrate account dispatch privileged extrinsics through a padded/collision-prone `EvmToSubstrate` mapping - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`on_accept` executes attached `SubstrateCalldata` after crediting the beneficiary. When `SubstrateCalldata.signature` is `Some`, it is cryptographically verified against the beneficiary's account and nonce. When it is `None`, verification is skipped entirely and the dispatch `origin` is instead derived from the message's `from` field via `T::EvmToSubstrate::convert`, whose default implementation is a naive zero-pad of the 20-byte EVM address into a 32-byte `AccountId`.

### Finding Description
In `modules/pallets/hyper-fungible-token/src/module.rs:124-187`, the optional-signature branch selects between two entirely different trust models: [1](#0-0) 

- If `signature` is provided, it is checked against `beneficiary_bytes`/`beneficiary` and the account nonce, so the resulting `origin == beneficiary`, cryptographically proven.
- If `signature` is `None`, no cryptographic check happens at all; the code falls straight to: [2](#0-1) 
which derives `origin` purely from the unauthenticated `message.from` bytes carried in the bridged payload, via `EvmToSubstrate::convert`. The default `EvmToSubstrate` implementation: [3](#0-2) 
zero-pads the 20-byte address into an `AccountId32`. This mapping collides with the standard Substrate `AccountId32` scheme used everywhere else in the runtime (any 32-byte account whose upper 12 bytes are zero looks identical to this derived account), so it is not namespaced/domain-separated per the bridge, per asset, or per source chain.

On the EVM side, `message.from` is reliably set to `abi.encodePacked(msg.sender)` at send time: [4](#0-3) 
so an attacker fully controls which `from` value is embedded, simply by calling `send()` themselves (or by controlling any address). The resulting `origin` is then used to `dispatch` an arbitrary `T::RuntimeCall`, gated only by the runtime's `BaseCallFilter`, not by any authorization tied to the beneficiary or destination-chain identity: [5](#0-4) 

This is the same class of bug as CVE-2021-31924: an optional credential (`SubstrateCalldata.signature`) is intended to authorize the action, but when the field is omitted, the code silently substitutes a much weaker "proof" (a bridge-message field asserting identity, never signed by a destination-chain key) and treats it as fully authorized for dispatching arbitrary calls "as" that derived account.

### Impact Explanation
Any address that can call `send()` on the paired EVM (or Substrate) contract can cause `pallet-hyper-fungible-token` to dispatch an arbitrary `RuntimeCall` as `RawOrigin::Signed(<AccountId32 derived from msg.sender>)` on the destination chain, without ever proving control of any destination-chain private key and without the beneficiary's consent. Because the derivation is a naive zero-pad (not namespaced), if any other part of the runtime, another bridge module, or a future feature also produces `AccountId32`s from zero-padded 20-byte identifiers (e.g. other EVM-compat pallets, precompiles, or governance-controlled derived/sovereign accounts) using the same convention, an attacker can pick an EVM address whose padded form pre-image-collides with a funded/privileged account and dispatch calls as that account — this is unauthorized-app-action and, depending on collisions, potential unbacked fund movement/privilege abuse. Even absent an exploitable collision today, the design intentionally allows dispatching arbitrary filtered calls "as" an account the attacker never proved control of on the destination chain, purely from data in an unsigned bridge message field — a forged-authorization class of bug reachable from a single `send()` transaction.

### Likelihood Explanation
High reachability: the path is triggered by any unprivileged caller of `HyperFungibleToken.send()` (or the Substrate `send` extrinsic) supplying non-empty `call_data` with `SubstrateCalldata.signature = None`. No relayer collusion, governance, or privileged role is needed — only a normal cross-chain token send with attached calldata reaching `on_accept`, which is exactly the "unprivileged token bridger" surface in scope.

### Recommendation
Do not allow a code path where omitting `signature` results in dispatching arbitrary runtime calls. Either:
1. Require `signature` to always be present and verified against the beneficiary before any `runtime_call.dispatch` (removing the `None` fallback path entirely), or
2. If a signature-less path is intentional (e.g., self-service calls "as the bridge-sender"), namespace the `EvmToSubstrate` conversion so it can never collide with organically-created `AccountId32`s (e.g., hash the address with a bridge-specific domain separator instead of zero-padding), and additionally scope/limit what such an unverified-origin call is permitted to do (e.g., restrict to non-custodial, self-referential actions only), rather than relying solely on `BaseCallFilter`.

### Proof of Concept
1. Attacker calls `HyperFungibleToken.send(params)` on the EVM source chain with `params.data = abi.encode([Call{...})` such that the SCALE-encoded destination payload is `SubstrateCalldata { signature: None, runtime_call: <arbitrary Call::encode()> }`. `from` in the resulting `Message` is automatically `msg.sender` (attacker's address): [6](#0-5) 
2. On delivery, `pallet-hyper-fungible-token::on_accept` decodes `SubstrateCalldata`, sees `signature = None`, and computes `origin = T::EvmToSubstrate::convert(H160(attacker_address))`: [2](#0-1) 
3. `runtime_call.dispatch(RawOrigin::Signed(origin))` executes, with the only defense being `BaseCallFilter::contains`: [5](#0-4) 
   No proof was ever required that the attacker controls any destination-chain key for `origin` — the identity was asserted only via the unsigned `from` field of the bridged message.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L124-187)
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L241-246)
```text
        bytes memory body = abi.encode(Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-282)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```
