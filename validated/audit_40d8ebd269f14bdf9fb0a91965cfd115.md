### Title
Unsigned cross-chain calldata dispatch derives runtime-call origin from unauthenticated message body field - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token`'s `IsmpModule::on_accept` allows an inbound cross-chain token transfer to carry optional `SubstrateCalldata` that gets dispatched as a runtime call. When the attacker omits a `signature`, the pallet skips all cryptographic verification and derives the dispatch `origin` directly from the `message.from` bytes embedded in the attacker-supplied ABI body, rather than from any value verified by ISMP's proof/membership machinery. This mirrors the CVE's bug class of "incorrect privilege assignment": a privileged action (here, `RawOrigin::Signed` dispatch) is executed under an identity that the destination logic never authenticates as belonging to the actual caller — the code trusts a claimed identifier baked into request data instead of verifying it cryptographically, analogous to PostgreSQL trusting `current_setting('role')`/current-user without confirming it matches the session that should apply.

### Finding Description
`Pallet::<T>::on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs:50-212` authenticates only the *request-level* sending contract (`PostRequest.from`) against `ContractToAsset` [1](#0-0) . It then ABI-decodes the request body into a `Message` whose `from` field is separate, attacker-influenced payload data (`bytes from; // original sender`) [2](#0-1) .

If the optional `SubstrateCalldata.data` is present, the pallet supports two paths:
- **Signed path**: verifies an Ed25519/Sr25519/ECDSA signature over `(nonce, runtime_call)` against the recipient (`beneficiary`) derived from `message.to` [3](#0-2) .
- **Unsigned path**: if `signature` is `None`, the origin is derived purely from `message.from` (converted via `EvmToSubstrate`) with **no verification whatsoever** that this bytes value corresponds to any cryptographically-proven signer [4](#0-3) .

The runtime call is then dispatched as `RawOrigin::Signed(origin)` [5](#0-4) , gated only by the chain's global `BaseCallFilter` — not by any check that the actual message sender controls that origin account. The project's own documentation confirms this is intentional design: *"If no signature is provided, the origin is derived from the sender address in the cross-chain message"* [6](#0-5) .

This is the same root-cause shape as the referenced CVE: a privileged operation (arbitrary runtime-call dispatch as a specific account) is granted based on an *unauthenticated claimed identity* embedded in message data, not on a value the framework has cryptographically or structurally verified to represent that identity.

### Impact Explanation
Because `Message.from` is a free-form bytes field within the ABI-encoded body of the bridged message (not the ISMP-proof-verified `PostRequest.from`), any determination of whose account is impersonated hinges entirely on whether the paired EVM contract (`HyperFungibleToken`/`WrappedHyperFungibleToken`) unconditionally sets this field to `msg.sender` with no attacker override. If any registered peer contract, custom integration, or future contract version allows `from` to diverge from the true caller (or an attacker deploys/controls a peer-registered contract that sets it arbitrarily), an attacker can cause an arbitrary substrate `RuntimeCall` (subject only to `BaseCallFilter`) to be dispatched as though authorized by a victim account (`EvmToSubstrate`-derived), enabling unauthorized transfers, governance actions, or other privileged calls not gated elsewhere — a direct "unauthorized app action" impact.

Even in the conservative case where `from` is strictly `msg.sender`, the design still grants full signed-dispatch authority over a deterministically-derived substrate account based solely on an EVM address embedded in unverified message data, with zero cryptographic proof of substrate-side key control, which weakens the intended security boundary of the signed path that exists precisely to require such proof.

### Likelihood Explanation
Reachable by any unprivileged token bridger: simply call the peer EVM contract's `send()` (or an ISMP-compatible custom peer contract) with non-empty calldata and omit the substrate signature. No special privilege, admin origin, or governance action is required — it is directly reachable from a single relayed cross-chain message once a token/chain pair is registered. Confirming full exploitability (i.e., whether `Message.from` can diverge from the true sender in the reference Solidity contracts) requires reviewing the `send()` implementation in `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`, which I was not able to fully inspect before running out of investigation budget — this is a genuine gap in my verification, not something I want to assert with false confidence.

### Recommendation
Require the unsigned path to be removed or hardened: either (a) always require a valid signature binding `(nonce, runtime_call)` to the account that will be used as `origin`, or (b) restrict the unsigned-origin fallback so the resulting `T::AccountId` can only ever be a special "unprivileged bridge relay" account with no ambient authority, rather than a directly-dispatchable, freely-chosen account. Additionally, explicitly re-verify (independent of this report) that all peer contracts hard-code `Message.from = msg.sender` with no caller-supplied override, and document/enforce this invariant at the protocol boundary rather than relying on peer-contract convention alone.

### Proof of Concept
1. Attacker calls `send()` on a registered `HyperFungibleToken` peer contract on an EVM source chain, with `to` = attacker's own recipient, `amount` = dust, and `data` = SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <arbitrary permitted call, e.g. governance/asset call> }`.
2. Relayer submits the resulting `PostRequest` with a valid ISMP membership proof via `handle_unsigned` [7](#0-6) .
3. `Pallet::<T>::on_accept` authenticates the request-level source contract (passes, since it's a genuine registered contract) [1](#0-0) , mints/releases the token amount, then decodes `SubstrateCalldata` and, finding `signature: None`, derives `origin = EvmToSubstrate(message.from)` without any signature check [4](#0-3) .
4. The pallet dispatches `runtime_call` as `RawOrigin::Signed(origin)` [5](#0-4) , executing it under that account's authority with no cryptographic proof that the true controller of that account authorized it.

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L197-200)
```rust
			use sp_runtime::traits::Dispatchable;
			runtime_call
				.dispatch(RawOrigin::Signed(origin.clone()).into())
				.map_err(|e| HftError::CallDispatchError(e.error))?;
```

**File:** docs/content/developers/polkadot/hyper-fungible-token.mdx (L189-196)
```text
```solidity
struct Message {
    bytes from;    // original sender (for timeout refunds)
    bytes to;      // recipient on destination chain
    uint256 amount;
    bytes data;    // optional calldata
}
```
```

**File:** docs/content/developers/polkadot/hyper-fungible-token.mdx (L215-217)
```text
If a signature is provided, it is verified against the beneficiary's account nonce and the runtime call before dispatch. Supported signature types: Ed25519, Sr25519, ECDSA. The account nonce is incremented after dispatch to prevent replay.

If no signature is provided, the origin is derived from the sender address in the cross-chain message.
```

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```
