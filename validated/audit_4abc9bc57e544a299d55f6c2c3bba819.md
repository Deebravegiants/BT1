This is significant. `on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs` mints/transfers tokens to the beneficiary **first** (lines 93-117), and only afterward, if `message.data` is non-empty, attempts to verify a signature and dispatch a `runtime_call` (lines 119-202). If the signature verification succeeds but `runtime_call.dispatch(...)` fails (line 198-200 `.map_err(HftError::CallDispatchError)`), the whole `on_accept` returns `Err`. This causes `pallet-ismp`'s request handler to delete the just-stored request receipt (`modules/ismp/core/src/handlers/request.rs:122-125`, "Delete receipt if module callback failed so it can be timed out"), which per the documented design (`docs/content/developers/polkadot/receiving.mdx:177-180`) explicitly makes the message **replayable** until it times out. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

Because the token credit (mint/transfer, lines 93-117) happens **before** the nonce-gated signature verification and dispatch (lines 119-202), and the nonce (`frame_system::Pallet::<T>::account_nonce(beneficiary)`, line 128) is only incremented on success (line 202), a relayer can force replay of the *entire* `on_accept` (including the credit step) simply by ensuring the calldata dispatch fails once (e.g. runtime call temporarily fails due to insufficient balance, filtered call, or any transient dispatch error unrelated to the credited funds) and re-delivering the same PostRequest/proof before it times out. Each successful replay mints/transfers the bridged amount to the beneficiary again, since the token-credit step is not idempotent and is not gated by any per-request/per-nonce guard beyond the overall ISMP request-receipt/timeout mechanism (which is explicitly non-durable on failure). This directly matches the reported bug class: "nonce not incremented on failure enables replay of an already-executed side effect against the user," except here the side effect is a mint/transfer of value rather than a signed meta-tx — and it is reachable by any relayer or attacker capable of submitting a duplicate `handle_unsigned`/proof for the same still-un-timed-out cross-chain message.

### Title
Non-idempotent token credit in `HyperFungibleToken::on_accept` is repeatedly re-executed on calldata-dispatch failure, enabling unbounded duplicate minting/transfer via message replay - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`on_accept` performs the token mint/transfer to the beneficiary before attempting to execute the optional embedded `runtime_call`. If that call dispatch fails, `on_accept` returns an error, which causes `pallet-ismp` to delete the request receipt it just stored, making the message eligible for replay until timeout, per the protocol's documented (but only safe when callbacks are idempotent) semantics.

### Finding Description
`Pallet::on_accept` (lines 50-212) executes in this order: (1) resolve the local asset for the source contract, (2) decode the cross-chain `Message`, (3) mint or transfer `amount` to `beneficiary` (lines 93-117), then (4) if `message.data` is non-empty, decode `SubstrateCalldata`, verify an off-chain signature keyed on `beneficiary`'s current `account_nonce`, and `dispatch` the embedded `runtime_call` (lines 119-202), incrementing the nonce only on success (line 202).

`pallet-ismp`'s request handler (`modules/ismp/core/src/handlers/request.rs:111-126`) stores a request receipt before invoking `on_accept`, and explicitly **deletes** that receipt if the module callback returns `Err`, "so it can be timed out" — i.e., so the message can be resubmitted. The protocol's own documentation (`docs/content/developers/polkadot/receiving.mdx:177-180`) states plainly: "The `IsmpHost` does not store receipts for failed messages... This effectively allows messages to be re-executed until they time out. Therefore you should ensure irreversible state changes occur only after a message effectively meets all success criteria."

`HyperFungibleToken::on_accept` violates this invariant: the irreversible state change (minting/transferring bridged value to `beneficiary`) happens *before* the operation that can fail (the calldata dispatch). Any failure in the calldata path — a filtered call (`BaseCallFilter`), insufficient balance/permissions for the dispatched `runtime_call`, or any other transient dispatch error — causes the entire handler to return `Err`, the receipt to be deleted, and the message to remain deliverable again. On the next delivery of the same underlying PostRequest/proof (before its timeout), the beneficiary is credited the bridged amount again, and the calldata section is retried.

### Impact Explanation
This allows an attacker (a relayer, or any unprivileged actor capable of resubmitting a valid membership proof for the same still-un-timed-out request) to trigger repeated unbacked minting/transfer of bridged value to the beneficiary account, simply by causing (or waiting for) the embedded calldata dispatch to transiently fail once and then repeatedly resubmitting the same request until timeout. Each successful `on_accept` re-execution credits `amount` again without any corresponding burn/lock event on the source chain, resulting in unbacked token inflation / permanent accounting mismatch between the source and destination chains — a direct violation of the bridge's backing invariant (unbacked mint), which is explicitly in scope per the validation rules.

### Likelihood Explanation
Likelihood is high in the general case where the message includes calldata: any dispatch failure in `runtime_call.dispatch(...)` (e.g., filtered call, insufficient recipient balance for a subsequent transfer_allow_death, or any other legitimate transient failure) is fully within the control or observation of a relayer, who only needs to resubmit the identical request. Because the request is not marked delivered on failure by design, no special privilege is needed to replay it — the request handler's dedup/duplicate checks (`request.rs:104-110`) only block replay after a *successful* `on_accept`.

### Recommendation
Reorder `on_accept` so all fallible operations (calldata decode, signature verification, base-call-filter check, and `runtime_call.dispatch`) occur and succeed *before* the token mint/transfer is performed, or make the credit step itself idempotent/guarded by a per-request commitment so repeated delivery of the same message cannot re-credit the beneficiary. At minimum, the mint/transfer and the calldata execution should be transactionally coupled such that a calldata-dispatch failure does not leave the credited funds in place while returning `Err` (which triggers replay-eligibility).

### Proof of Concept
1. Source chain locks/burns `amount` and dispatches a PostRequest to `HyperFungibleToken` with non-empty `message.data` containing a `SubstrateCalldata` whose `runtime_call` will predictably fail on first delivery (e.g., a `Balances::transfer_allow_death` to a receiver with insufficient existing balance/ED, or any call temporarily blocked by `BaseCallFilter`).
2. Relayer submits the request via `handle_unsigned`; `pallet-ismp`'s handler stores the request receipt, then calls `on_accept`, which credits `beneficiary` with `amount` (line 93-117) then attempts the `runtime_call.dispatch` which fails (line 198-200), causing `on_accept` to return `Err`.
3. `request.rs:122-125` deletes the just-stored receipt, since the callback failed.
4. Relayer resubmits the identical `PostRequest` (same proof/commitment, not yet timed out); `on_accept` runs again, crediting `beneficiary` a second time with the same `amount`, again failing calldata dispatch (or succeeding this time, but the first credit was still an extra, unbacked mint).
5. Repeat until timeout window closes; each iteration adds another unbacked credit to `beneficiary` with no corresponding lock/burn event on the source chain.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L93-117)
```rust
		// Mint or transfer to beneficiary
		if local_asset_id == T::NativeAssetId::get() {
			<T as Config>::NativeCurrency::transfer(
				&Pallet::<T>::pallet_account(),
				&beneficiary,
				amount,
				ExistenceRequirement::AllowDeath,
			)
			.map_err(|e| HftError::TransferFailed(e.into()))?;
		} else {
			let is_native = NativeAssets::<T>::get(local_asset_id.clone());
			if is_native {
				<T as Config>::Assets::transfer(
					local_asset_id,
					&Pallet::<T>::pallet_account(),
					&beneficiary,
					amount.into(),
					Preservation::Expendable,
				)
				.map_err(|e| HftError::TransferFailed(e.into()))?;
			} else {
				<T as Config>::Assets::mint_into(local_asset_id, &beneficiary, amount.into())
					.map_err(|e| HftError::MintFailed(e.into()))?;
			}
		}
```

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

**File:** modules/ismp/core/src/handlers/request.rs (L111-126)
```rust
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
				});
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
				Ok(res)
```

**File:** docs/content/developers/polkadot/receiving.mdx (L175-180)
```text
## Security Considerations

<Callout title={'Replay Attack Warning'} type={"warn"}>

The `IsmpHost` does not store receipts for failed messages. ie messages whose `IsmpModule` returns `Err`. This effectively allows messages to be re-executed until they time out. **Therefore you should ensure irreversible state changes occur only after a message effectively meets all success criteria**.
</Callout>
```
