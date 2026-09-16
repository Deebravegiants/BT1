## Title
Cross-Chain Replay of `pallet-hyper-fungible-token` Calldata-Execution Signatures Due to Missing Domain Separation - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`pallet-hyper-fungible-token`'s `on_accept` handler decodes an attacker-supplied `SubstrateCalldata { signature, runtime_call }` from the incoming cross-chain `Message.data` field and, if a signature is present, verifies it against `keccak256((account_nonce, runtime_call).encode())` before dispatching the arbitrary `runtime_call` as `RawOrigin::Signed(beneficiary)`. The signed payload contains **no domain separator** — no genesis hash, chain ID/`StateMachine`, spec version, or pallet instance identifier — so a signature authorizing a runtime call on one chain deployment of this pallet is also valid on any other chain deployment where the same account happens to share the same nonce. [1](#0-0) 

### Finding Description
The relevant flow is:
1. `send()` on the pallet lets any signed user embed arbitrary `call_data` (which becomes `Message.data`) destined for a specific `StateMachine`. [2](#0-1) 
2. On the receiving chain, `on_accept` decodes `SubstrateCalldata` and, when a `signature` is supplied, computes the signed message as `(nonce, runtime_call).encode()` hashed with `keccak_256`, verified against the recovered/derived key for `beneficiary` — with the account nonce as the *only* replay-protection input. [3](#0-2) 
3. After verification, the pallet dispatches the decoded `RuntimeCall` as `RawOrigin::Signed(beneficiary)`, subject only to `BaseCallFilter`, and increments the account nonce. [4](#0-3) 

Because the signed preimage is only `(nonce, runtime_call)` with no chain-specific salt, the exact same `(signature, runtime_call)` pair embedded in `SubstrateCalldata` remains valid on **every other chain** running `pallet-hyper-fungible-token` for the same beneficiary account, as long as that account's current nonce on the target chain matches the nonce used in the signature. Substrate account public keys (and therefore `AccountId`s) are frequently identical across parachains for a given user (same seed/derivation), and account nonces frequently start at (or return to) small values such as 0/1/2 for freshly-funded or infrequently used accounts, making nonce collisions realistic — especially since the nonce is visible on-chain and attacker-controllable in timing (the attacker only needs to wait for/target an account whose nonce matches).

An unprivileged attacker (any user able to invoke `send`/relay a cross-chain message through the token bridge) who obtains a previously-broadcast `(signature, runtime_call)` pair (e.g., observed from an earlier legitimate cross-chain transfer, or a signature the victim shared believing it was scoped to one specific destination) can re-submit it as `call_data` targeting a different destination chain where the same account/nonce combination exists, causing an unauthorized `RuntimeCall` to be dispatched as that victim's origin.

This is directly analogous to the reported n8n class of bug: an authenticated/permissioned action (there: Git-node code execution; here: signed calldata dispatch) that lacks sufficient contextual/scope binding, enabling execution outside its intended trust boundary.

### Impact Explanation
Successful replay causes an arbitrary `RuntimeCall` (subject to `BaseCallFilter`) to execute as the victim's account on an unintended chain. Depending on what calls the runtime permits (transfers, staking, governance voting, pallet-specific privileged calls the victim holds authority over, etc.), this can result in unauthorized transfer/movement of the victim's assets or unauthorized state-changing actions performed in their name — a direct "unauthorized app action" per the standard this program treats as Critical/High impact. Because dispatch happens with the beneficiary's own signing authority, any asset or capability that account controls on the target chain is exposed.

### Likelihood Explanation
Exploitability depends on the attacker acquiring a valid `(signature, runtime_call)` pair and finding a target chain/account/nonce match, so it is not trivially exploitable against an arbitrary victim at will. However, it is systemic: the vulnerability exists in the "convenience feature" advertised to integrators (`docs/content/developers/polkadot/hyper-fungible-token.mdx`) as safe cross-chain calldata execution, and any relayer or observer of on-chain data can capture and replay such signatures across every chain deployment sharing the account. Given Hyperbridge's multi-chain design (the pallet is meant to be deployed on many parachains simultaneously, exactly the scenario that maximizes nonce-collision odds), this is a realistic and moderately likely occurrence rather than a purely theoretical one.

### Recommendation
Bind the signed payload to the specific execution context by including a domain separator in the signed preimage, e.g. `(genesis_hash_or_state_machine_id, nonce, runtime_call).encode()`, mirroring standard EIP-712-style domain separation already used elsewhere in the codebase (e.g., `IntentsBase.sol`'s `_hashTypedDataV4`). At minimum, include the destination `StateMachine`/chain identifier and a pallet-instance/genesis discriminator so a signature cannot be replayed across independent deployments.

### Proof of Concept
1. Victim signs `SubstrateCalldata { signature: Some(sig), runtime_call: call_bytes }` where `sig` is `Ed25519/Sr25519/Ecdsa` over `keccak_256((nonce_N, call_bytes).encode())`, intending it to execute exactly once on Chain A via `pallet-hyper-fungible-token::on_accept`.
2. This calldata is embedded in `Message.data` and dispatched from an EVM source chain to Chain A; `on_accept` verifies the signature against `account_nonce(beneficiary)==N` on Chain A and dispatches `call_bytes`, then increments the nonce to `N+1`.
3. An attacker who has observed `sig` and `call_bytes` (e.g. from Chain A's public block data) submits a new cross-chain transfer through the same `HyperFungibleToken` bridge machinery to Chain B, a separate deployment of `pallet-hyper-fungible-token`, setting `Message.data` to the identical `SubstrateCalldata{ signature: sig, runtime_call: call_bytes }`.
4. If the same `beneficiary` `AccountId` exists on Chain B with `account_nonce == N` (plausible for a lightly used or freshly provisioned account), `on_accept` on Chain B recomputes the same `keccak_256((N, call_bytes).encode())` hash, the signature verifies successfully, and `call_bytes` is dispatched as `RawOrigin::Signed(beneficiary)` on Chain B — an action the victim never authorized for Chain B. [5](#0-4)

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

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L292-310)
```rust
			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

			let token_message = Message {
				from: sender.to_vec().into(),
				to: params.recipient.to_vec().into(),
				amount: alloy_primitives::U256::from_be_bytes(erc20_amount.to_big_endian()),
				data: params.call_data.unwrap_or_default().into(),
			};

			let dispatch_post = DispatchPost {
				dest: params.destination,
				from: PALLET_ID.to_bytes(),
				to: token_contract,
				timeout: params.timeout,
				body: Message::abi_encode(&token_message),
			};
```
