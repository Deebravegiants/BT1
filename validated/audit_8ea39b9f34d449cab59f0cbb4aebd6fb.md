### Title
Cross-chain replay of HFT calldata-execution signatures due to missing chain/destination binding - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`hyper-fungible-token`'s `on_accept` handler executes an arbitrary `RuntimeCall` on behalf of a beneficiary when a cross-chain token transfer carries optional calldata with a signature. The signed payload is only `(nonce, runtime_call)` — it omits any binding to the destination chain, the source contract/state machine, or the HFT deployment itself. A signature a user creates to authorize a call on one chain can therefore be replayed verbatim on any other chain running the same pallet where the beneficiary's account nonce happens to match, letting an attacker forge execution of that call on a chain the user never intended.

### Finding Description
In `on_accept`, when `message.data` is non-empty and carries a signature, the module reconstructs the signed payload as: [1](#0-0) 

for Ed25519/Sr25519, and with an Ethereum-prefixed variant for ECDSA: [2](#0-1) 

None of these payloads include: the destination `StateMachine`/chain id, the source contract address (`from`)/`source` state machine that authenticated the transfer via `ContractToAsset`, or any pallet/module-specific domain separator. The only replay defense is `frame_system::Pallet::<T>::account_nonce(beneficiary)`, which is the beneficiary's *local, per-chain* system nonce — for a fresh or rarely-used account this is `0` (or matches) across many chains simultaneously, since the pallet is explicitly designed to run identically across "multiple supported chains" as part of a multichain bridge (mirroring the exact quote cited in the external report).

By contrast, the sibling relayer pallet's equivalent signed payload explicitly folds in `dest_chain` to prevent exactly this class of bug: [3](#0-2) 

and its test suite specifically exercises rejecting a signature captured for a different chain: [4](#0-3) 

`hyper-fungible-token::on_accept` has no analogous check. The `Message`/`SubstrateCalldata` blob (which contains the signature and the encoded `RuntimeCall`) is embedded by the user when initiating the cross-chain transfer on the source chain, and is visible to anyone (in the source transaction, or via the eventual ISMP `PostRequest` body) before/while it is relayed. An attacker who observes this payload can construct a new `PostRequest` targeting a *different* destination chain that runs the same `hyper-fungible-token` pallet, using any `(source, from)` pair registered in that chain's `ContractToAsset` map, with the beneficiary set to the same account (same public key, valid across substrate chains) and the identical signature+`runtime_call` bytes. If the beneficiary's nonce on that other chain also happens to be at the signed value (trivially true for `0`, the default for any account that hasn't yet transacted there), `on_accept` will verify the signature successfully and dispatch the `runtime_call` as `RawOrigin::Signed(beneficiary)` — executing an operation the user never authorized on that chain.

### Impact Explanation
This allows unauthorized dispatch of arbitrary runtime calls (subject only to `BaseCallFilter`) as an unwitting user's account on a chain other than the one the user intended, using a signature that was never meant to be valid there. Depending on the call encoded (e.g. `Balances::transfer`, approvals, staking operations, or another HFT call), this can lead to direct loss of funds or unauthorized privileged actions performed under the victim's identity — a concrete "unauthorized app action" / theft-of-funds impact reachable by any unprivileged relayer or observer of the cross-chain payload, matching the Medium-severity class of the reported analog.

### Likelihood Explanation
The precondition (matching nonce, valid `runtime_call` decode, filter pass, and same beneficiary AccountId existing/registering on another HFT-enabled chain) is realistic: nonces of freshly funded beneficiary accounts commonly start at `0` on every chain, substrate AccountIds (raw public keys) are naturally shared across parachains, and the HFT pallet is explicitly intended to be deployed on "multiple supported chains" against the same source contracts. No privileged access is required — only observing a legitimately-relayed calldata-carrying transfer and re-submitting an ISMP request with the same body to a different destination.

### Recommendation
Bind the signed payload to the specific execution context, mirroring the pattern already used in `pallet-relayer`:
- Include the destination `StateMachine` (or a genesis-hash/chain-id equivalent), the `source` state machine and `from` contract address (or the HFT module identifier), and ideally the request `commitment`, inside the hashed payload for all three (`Ed25519`, `Sr25519`, `Ecdsa`) branches.
- Consider replacing/augmenting the generic `frame_system` nonce with a dedicated per-(beneficiary, source-chain) replay-protection counter or a commitment-based one-time-use marker, so a captured signature cannot be reused across chains or reprocessed after the intended nonce naturally advances elsewhere.

### Proof of Concept
1. User on source chain (e.g. Ethereum) calls the bridge contract to send tokens to `beneficiary` on destination chain A, with `message.data` = `SubstrateCalldata { runtime_call: C, signature: S }`, where `S` = `ed25519_sign(beneficiary_key, keccak256(encode(nonce=0, C)))`.
2. This `message.data` is visible in the source transaction/request body before/while relaying.
3. Attacker crafts a new ISMP `PostRequest` with `source`/`from` registered in `ContractToAsset` on destination chain B (also running `hyper-fungible-token`), `to = beneficiary` (same public key/AccountId), and `body` containing a `Message` whose `data` field is the identical `SubstrateCalldata { runtime_call: C, signature: S }`.
4. On chain B, `beneficiary`'s account nonce is `0` (fresh account). `on_accept` recomputes `keccak256(encode(0, C))`, verifies against `S` successfully (since the payload never encoded chain/destination context), and dispatches `C` as `RawOrigin::Signed(beneficiary)` on chain B — executing a call the user only authorized for chain A. [5](#0-4)

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

**File:** modules/pallets/relayer/src/outbound_request.rs (L201-209)
```rust
/// the on-chain `commitment` tag in [`crate::pallet::OutboundRequestsClaimed`], so a
/// captured signature can't be reused once the commitment is claimed.
pub fn outbound_request_delivery_message(
	commitment: H256,
	dest_chain: StateMachine,
	payee: [u8; 32],
) -> [u8; 32] {
	sp_io::hashing::keccak_256(&(commitment, dest_chain, payee).encode())
}
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp_relayer.rs (L879-884)
```rust
		// A signature the relayer would have produced for a different source chain.
		// The byte payload is reused as if captured from that chain and replayed here.
		let foreign_chain = StateMachine::Kusama(7777);
		let signature = pair
			.sign_prehashed(&beneficiary_message(0, foreign_chain, beneficiary_address.as_bytes()))
			.to_vec();
```
