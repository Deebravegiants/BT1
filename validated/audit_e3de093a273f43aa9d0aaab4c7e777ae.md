### Title
Unsigned cross-chain calldata dispatches with `RawOrigin::Signed` derived from a forgeable `Message.from` field, letting a bridging transfer impersonate an unrelated account - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler lets an inbound ERC20-bridging message carry optional calldata that is dispatched on the destination substrate chain as if it were signed by a specific account. When the message includes a `SubstrateCalldata.signature`, that signature is cryptographically verified against `beneficiary` (the mint recipient). But when `signature` is `None`, the dispatch origin is derived directly from the unauthenticated `message.from` bytes embedded in the ABI-encoded payload, with no proof of key ownership at all.

### Finding Description
In `on_accept`, the pallet authenticates only the outer `PostRequest` pairing `(source, from)` against `ContractToAsset` — i.e., that the message came from the registered token contract address on a known chain [1](#0-0) . It never authenticates the *inner* `message.from` field of the ABI-decoded `Message { from, to, amount, data }` struct [2](#0-1)  — that field is attacker-controlled input chosen by whoever calls the send function on the source-chain token contract.

When optional calldata is attached and no `SubstrateCalldata.signature` is supplied, the pallet computes the dispatch origin straight from this unauthenticated `message.from`: [3](#0-2) 

and then dispatches the attacker-supplied runtime call as `RawOrigin::Signed(origin)`: [4](#0-3) 

Contrast this with the signed path, which properly recovers/verifies a signature over `(nonce, runtime_call)` and checks it resolves to `beneficiary` before allowing dispatch [5](#0-4) . The unsigned fallback has no equivalent proof: any address bytes placed in `message.from` become the signer of an arbitrary runtime call. Because `handle_unsigned`/message delivery on ISMP is permissionless (anyone with a valid proof can relay), a single relayed cross-chain transfer message — crafted by anyone who can call the registered token contract on the source chain with `from` set to a victim's substrate address (or an EVM address that maps to the victim via `EvmToSubstrate`) — results in a runtime call being executed under `RawOrigin::Signed(victim)` on the destination chain, without the victim's consent or any signature from them. This mirrors the CVE's bug class: an endpoint intended to be reachable only via a directly-authenticated session/owner is instead reachable through a delegated/relayed channel that lets the caller act on an unrelated account's behalf.

### Impact Explanation
This is unauthorized-app-action / account impersonation: an attacker can force arbitrary runtime calls (subject only to `BaseCallFilter`) to execute as if signed by any victim account they choose, using nothing but a self-crafted `from` field in a bridging message. Depending on which calls the runtime's `BaseCallFilter` permits, this can enable unauthorized transfers, staking/voting actions, approvals, or other privileged operations performed "as" the victim — a direct violation of account-authorization boundaries, matching the CVSS characterization of the analog CVE (integrity impact via forged authorization, no confidentiality/availability impact).

### Likelihood Explanation
Reachable from a single cross-chain message dispatch: the attacker only needs to call the registered `HyperFungibleToken`/`WrappedHyperFungibleToken` contract's send function on any connected source chain with `data` encoding `SubstrateCalldata { signature: None, runtime_call: <victim-affecting call> }` and `from` set to the target victim's address bytes. No relayer collusion or privileged role is required — pallet-ismp's unsigned message delivery is explicitly permissionless by design. The only friction is whatever calls survive `BaseCallFilter`, and whether the destination account (`origin`) needs to already exist/hold funds for the dispatched call to have an effect.

### Recommendation
Require an authenticated proof of ownership for the unsigned path as well, or remove it entirely: either mandate a valid `SubstrateCalldata.signature` whenever `data` is non-empty (eliminating the unauthenticated fallback), or restrict the "no signature" case to only permit calls where `origin` is inherently safe (e.g., `RawOrigin::None`/unsigned-style handling instead of `RawOrigin::Signed`), so no runtime call can ever be attributed to a victim account without that account's cryptographic consent.

### Proof of Concept
1. Attacker calls the source-chain `HyperFungibleToken` contract's transfer/send function, setting the encoded `Message.data` to a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <victim-affecting call, e.g. Balances::transfer_all or a governance vote> }`, and `Message.from` to the victim's account bytes (32-byte substrate AccountId, or a 20-byte EVM address whose `EvmToSubstrate::convert` maps to the victim).
2. Any relayer delivers this message; `pallet_ismp` verifies the standard state/consensus proof (this succeeds normally since the attacker's transaction is genuinely included on the source chain) and routes to `HyperFungibleToken::on_accept`.
3. `on_accept` authenticates only `(source, from=contract address)` via `ContractToAsset`, passes, mints/transfers tokens to whatever `message.to` beneficiary the attacker chose, then reaches the calldata branch.
4. Since `substrate_data.signature` is `None`, `origin` is set to the victim's `AccountId` derived from the attacker-supplied `message.from` [3](#0-2) .
5. `runtime_call.dispatch(RawOrigin::Signed(origin))` executes the attacker's chosen call as the victim, with no signature from the victim ever checked [4](#0-3) .

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L54-56)
```rust
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L197-202)
```rust
			use sp_runtime::traits::Dispatchable;
			runtime_call
				.dispatch(RawOrigin::Signed(origin.clone()).into())
				.map_err(|e| HftError::CallDispatchError(e.error))?;

			frame_system::Pallet::<T>::inc_account_nonce(origin);
```

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L33-43)
```rust
// ABI-compatible Message matching the Solidity HyperFungibleToken.Message struct:
// struct Message { bytes from; bytes to; uint256 amount; bytes data; }
alloy_sol_macro::sol! {
	#![sol(all_derives)]
	struct Message {
		bytes from;
		bytes to;
		uint256 amount;
		bytes data;
	}
}
```
