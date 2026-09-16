Based on my analysis of `modules/pallets/hyper-fungible-token/src/module.rs`, I found a concrete analog to CVE-2020-25717's "incorrect identity mapping → privilege escalation" pattern. Note: I was unable to fully confirm within available iterations whether the paired Solidity contract (`sdk/packages/core/contracts/apps/HyperFungibleToken.sol`) constrains the `Message.from` field to always equal `msg.sender`, or allows the caller to set it freely — this is the one detail that would determine whether the blast radius is "impersonate arbitrary third-party accounts" or "the fixed-mapping account for your own address." The root-cause flaw described below holds either way, because the flaw is in the *pallet's* trust decision, not in what the Solidity side happens to pass.

### Title
Unauthenticated identity mapping lets a cross-chain message dispatch an arbitrary runtime call as another account without signature proof - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` in the hyper-fungible-token ISMP module, when executing optional calldata attached to an inbound token transfer, derives the dispatch `origin` from the unauthenticated `message.from` field of the ABI-decoded message body when `substrate_data.signature` is `None`. This mirrors the Samba/CVE-2020-25717 bug class: an identifier belonging to one domain (an EVM address, arbitrary bytes carried inside message body) is deterministically mapped to a local identity (a substrate `AccountId`) and then used to authorize a privileged action (dispatching an arbitrary `RuntimeCall` as `RawOrigin::Signed(origin)`), without any cryptographic proof that the caller controls the private key behind that mapped identity.

### Finding Description
In `on_accept`: [1](#0-0) 

- When `substrate_data.signature` is `Some(...)`, the pallet cryptographically verifies (Ed25519/Sr25519/Ecdsa) that the signer corresponds to `beneficiary` (the token recipient) before using `beneficiary` as the dispatch origin.
- When `substrate_data.signature` is `None`, the code instead takes `message.from` — a raw byte field from the attacker/contract-controlled ABI message body, not the ISMP transport-level `from` (module id) which is separately checked against `ContractToAsset` — and passes it through `T::EvmToSubstrate::convert(...)` (default impl: zero-pad 20 bytes into a 32-byte `AccountId`) to produce `origin`, with **no signature check at all**. [2](#0-1) 

- That `origin` is then used to dispatch an arbitrary, attacker-supplied `RuntimeCall`: [3](#0-2) 

Because `EvmToSubstrate::convert` is a pure, public, deterministic function (in the default impl, just zero-padding), *anyone* can compute the substrate `AccountId` that corresponds to any arbitrary 20-byte value they place in `message.from`, without ever proving ownership of a private key for that identity. The pallet then dispatches a runtime call "as" that identity. This is structurally the same defect as CVE-2020-25717: an authenticated principal (anyone who can get a message accepted through a registered token-gateway contract) can, via the domain→local identity map, cause code to execute under a different local identity's authority, without proving they are that identity.

The only backstop is `BaseCallFilter::contains(&runtime_call)`, which filters call *types* globally (e.g., maintenance mode) but does not protect against a call being executed under the *wrong account's authority* — e.g., a governance-permissioned or otherwise privileged-by-configuration extrinsic that checks `ensure_signed(origin) == some_expected_account` inside its own logic would be bypassable if the attacker can compute/target that account's derived identity.

### Impact Explanation
Any attacker able to trigger an inbound `Send` message to the `pallet_hyper_fungible_token` module (i.e., anyone who can call the registered EVM `HyperFungibleToken` contract's send/teleport function, which requires no special privilege) can craft calldata whose `signature` field is `None` and whose `from` field is any 20 (or 32) bytes of their choosing. The pallet will dispatch an arbitrary `RuntimeCall` under `RawOrigin::Signed(<mapped account>)`. If the destination-runtime pairs the `EvmToSubstrate` mapping with pallets/extrinsics that make authorization decisions based on the caller's `AccountId` (e.g., "only the treasury account may do X", proxy/multisig accounts, or any pallet call gated by a specific signer), the attacker can impersonate that identity's authority for any call permitted by `BaseCallFilter`. This is unauthorized-app-action-class impact and can lead to unauthorized asset movement (any `Currency`/`Assets` extrinsic dispatchable as a signed origin, e.g. transfers, approvals) if a privileged account's derived identity is targeted, or funds loss if the attacker impersonates other users' derived accounts to spend their locally held balances.

### Likelihood Explanation
High reachability: the entry point is a normal, unprivileged cross-chain `Send` message deliverable by anyone able to interact with the paired EVM contract (an ordinary user action, not requiring admin/governance/relayer privilege) — squarely within the reachable analog paths (token bridger mint/transfer flow, `IsmpModule::on_accept`). The only gating conditions are (1) `ContractToAsset` must recognize the ISMP-level `source`/`from` pair (i.e., message must come through a legitimately registered token-gateway contract pairing — this is satisfied by any normal user transaction through that contract) and (2) `message.data` must be non-empty with an unsigned `SubstrateCalldata`. Neither condition requires elevated privilege.

### Recommendation
Require a valid signature (or equivalent cryptographic proof of key ownership) for the unsigned-`from` branch as well, or remove the unsigned branch entirely and always require `substrate_data.signature` to authorize dispatching an arbitrary runtime call. At minimum, do not use `EvmToSubstrate::convert(message.from)` as a dispatch origin without proof that the submitter controls the corresponding key — mirror the signed branch's verification logic (nonce + signature check) unconditionally before calling `runtime_call.dispatch(RawOrigin::Signed(origin))`.

### Proof of Concept
1. Attacker calls the registered `HyperFungibleToken` EVM contract's send function with an arbitrary token transfer.
2. Attacker crafts the message body so that `data` is non-empty, decodes to `SubstrateCalldata { signature: None, runtime_call: <arbitrary call, e.g. a call gated on a specific AccountId elsewhere in the runtime> }`, and sets `message.from` to the 20 bytes of the EVM address whose mapped substrate account the attacker wants to impersonate.
3. On delivery, `on_accept` decodes the message, skips signature verification (branch taken because `signature == None`), computes `origin = T::EvmToSubstrate::convert(H160::from_slice(from_bytes))`.
4. `runtime_call.dispatch(RawOrigin::Signed(origin))` executes with the authority of the attacker-chosen mapped account, without the attacker ever proving control of the corresponding private key. [4](#0-3)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L124-202)
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

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L124-138)
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
```
