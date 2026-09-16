## Analysis: Missing chain/domain binding in `pallet-hyper-fungible-token`'s calldata authorization signature

The reported bug class (EIP-712 signature verification that omits chain-id binding, enabling cross-chain replay) has a direct analog in `pallet-hyper-fungible-token`'s optional calldata-execution path.

### Title
Missing chain/domain binding in signed `SubstrateCalldata` payload allows cross-chain replay of authorized runtime calls - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
When a `HyperFungibleToken` cross-chain transfer includes optional `data`, the pallet decodes a `SubstrateCalldata { signature, runtime_call }` and, if a signature is present, verifies it against a payload built only from `(nonce, runtime_call)` — with no chain identifier, genesis hash, destination `StateMachine`, or contract/pallet address included in the signed message. This mirrors the reported Forwarder bug: a signature intended to authorize one specific execution context can be replayed wherever the same "domain" parameters (here: account nonce) happen to coincide.

### Finding Description
In `on_accept`, when `message.data` is non-empty, the pallet builds the signing payload as: [1](#0-0) 

For all three signature schemes (Ed25519, Sr25519, ECDSA) the exact same payload shape is hashed and verified: [2](#0-1) 

The only "domain-separating" input is `frame_system::Pallet::<T>::account_nonce(beneficiary)` — read fresh from the destination chain's own storage — and the `runtime_call` bytes themselves. There is no inclusion of:
- the destination `StateMachine`/chain id,
- a genesis hash or pallet-instance identifier,
- the source chain (`source`) the message arrived from,
- any Hyperbridge request commitment or nonce tied to the specific cross-chain message.

This differs fundamentally from `pallet-ismp-relayer`'s signed messages elsewhere in the codebase, which explicitly bind the destination `StateMachine` into the hashed payload, e.g. `outbound_request_delivery_message`: [3](#0-2) 
and `beneficiary_message`: [4](#0-3) 

Both of those explicitly fold `state_machine`/`dest_chain` into the signed digest for exactly the reason the reported bug describes — to prevent a signature valid on one chain from being replayed on another. `pallet-hyper-fungible-token`'s calldata-authorization path lacks this binding entirely.

### Impact Explanation
Because `frame_system` account nonces are local per-chain state and default to `0` for any account that has never submitted an extrinsic (which is the common case for a beneficiary receiving its first cross-chain transfer), the same `(nonce=0, runtime_call)` signature is valid simultaneously on:
- multiple parachains/runtimes that both integrate `pallet-hyper-fungible-token` with the same `RuntimeCall` encoding,
- a forked/re-launched chain (testnet reset, chain migration) where nonces reset,
- any future or parallel deployment sharing the same call-index layout.

An attacker (or the original relayer/anyone forwarding the cross-chain message body, since this path is reached via `IsmpModule::on_accept` off of an ordinary token-transfer message anyone can trigger by sending tokens with `data` set) can capture a user's signed `SubstrateCalldata` from one chain's transaction/mempool and resubmit the identical `message.data` embedded in a new (or replayed) `PostRequest`/token transfer to a different chain (or the same chain post-nonce-reset), causing the signed `runtime_call` to dispatch there under the user's identity without their consent for that specific chain. Depending on `runtime_call` contents (e.g. `Balances::transfer`, staking, governance votes) this is unauthorized-action / unbacked-state-change class impact — the call executes with `RawOrigin::Signed(beneficiary)` on a chain the user never intended, and `frame_system::Pallet::<T>::inc_account_nonce` only prevents replay on the *same* chain instance, not across chains.

### Likelihood Explanation
The signature is user-attached, off-chain-computed, application-level data traveling inside message.data of a permissionless HyperFungibleToken message; it does not depend on any protocol-level replay protection Hyperbridge otherwise provides for request commitments (those protect against re-delivery of the same ISMP request, not against reuse of the *application payload* embedded in a *new* request/message on a different chain). Any environment running two or more instances of this pallet (mainnet/testnet, multiple parachains, or a chain reset) is directly exploitable with a captured signature and no special privilege.

### Recommendation
Bind the signed `SubstrateCalldata` payload to the destination chain and this specific delivery, analogous to `outbound_request_delivery_message`/`beneficiary_message`. Include at minimum: the destination `StateMachine` id (or a chain-specific domain identifier such as `frame_system::Pallet::<T>::block_hash(0)` / genesis hash), and ideally the originating ISMP request commitment, in the hashed payload before recovery/verification in `modules/pallets/hyper-fungible-token/src/module.rs`. This ensures a signature authorizing a runtime call is scoped to exactly one chain and one delivery.

### Proof of Concept
1. User signs `SubstrateCalldata { signature: Some(sig over keccak256(nonce=0 ‖ runtime_call)), runtime_call }` intending it for Chain A's `HyperFungibleToken::send` with `call_data` set.
2. Attacker observes this signed payload (public mempool/relayer traffic) and, before/without the user's consent, submits an equivalent cross-chain token message (via HyperFungibleToken contract on the EVM side, or directly crafting the ISMP `PostRequest`) addressed to Chain B, embedding the identical `message.data` (same `nonce`, same `runtime_call`, same signature).
3. On Chain B, `beneficiary`'s `account_nonce` is `0` (fresh account), so `on_accept`'s signature check passes identically, and `runtime_call.dispatch(RawOrigin::Signed(beneficiary))` executes on Chain B — a context the user never authorized — demonstrated by `should_receive_asset_with_calldata` showing same-chain replay is blocked only via nonce increment, with no chain-binding check anywhere in the verified payload: [5](#0-4)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L128-133)
```rust
				let nonce = frame_system::Pallet::<T>::account_nonce(beneficiary.clone());

				match multi_signature {
					MultiSignature::Ed25519(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let msg = sp_io::hashing::keccak_256(&payload);
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L142-171)
```rust
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
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L203-209)
```rust
pub fn outbound_request_delivery_message(
	commitment: H256,
	dest_chain: StateMachine,
	payee: [u8; 32],
) -> [u8; 32] {
	sp_io::hashing::keccak_256(&(commitment, dest_chain, payee).encode())
}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L309-315)
```rust
pub fn beneficiary_message(
	nonce: u64,
	state_machine: StateMachine,
	beneficiary: &[u8],
) -> [u8; 32] {
	sp_io::hashing::keccak_256(&(nonce, state_machine, beneficiary).encode())
}
```

**File:** modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs (L280-321)
```rust
		// Sign with sr25519
		let (pair, ..) = sp_core::sr25519::Pair::generate();
		let beneficiary_bytes = pair.public().0;
		let payload = (0u64, runtime_call.clone()).encode();
		let message_hash = sp_io::hashing::keccak_256(&payload);
		let raw_signature = pair.sign(&message_hash);
		let multisignature = MultiSignature::Sr25519(raw_signature).encode();

		let substrate_data = SubstrateCalldata { signature: Some(multisignature), runtime_call };

		let module = HyperFungibleToken::default();
		let post = PostRequest {
			source: StateMachine::Evm(1),
			dest: StateMachine::Kusama(100),
			nonce: 0,
			from: hft_contract(),
			to: pallet_hyper_fungible_token::PALLET_ID.to_bytes(),
			timeout_timestamp: 1000,
			body: {
				let msg = Message {
					from: alloy_primitives::Bytes::from(vec![0x11u8; 20]),
					to: alloy_primitives::Bytes::from(beneficiary_bytes.to_vec()),
					amount: {
						let bytes = convert_to_erc20(SEND_AMOUNT, 18, 10).to_big_endian();
						alloy_primitives::U256::from_be_bytes(bytes)
					},
					data: alloy_primitives::Bytes::from(substrate_data.encode()),
				};
				Message::abi_encode(&msg)
			},
		};

		module.on_accept(post.clone()).unwrap();

		// The calldata transferred tokens from beneficiary to final_recipient
		let final_balance = pallet_balances::Pallet::<Test>::free_balance(final_recipient);
		assert_eq!(final_balance, SEND_AMOUNT);

		// Replay should fail (nonce incremented)
		let result = module.on_accept(post);
		assert!(result.is_err());
	});
```
