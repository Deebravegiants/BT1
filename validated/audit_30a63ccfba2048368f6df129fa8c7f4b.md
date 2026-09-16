### Title
HFT calldata signature check uses the beneficiary's own on-chain nonce, letting the beneficiary self-invalidate delivery after tokens are already minted, enabling a double-mint via timeout - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`HyperFungibleToken.on_accept` mints/transfers the bridged amount to the beneficiary **before** verifying the optional calldata's signature, and that signature is checked against the beneficiary's *live* `frame_system::account_nonce`. Because the beneficiary fully controls when their own nonce advances (any ordinary extrinsic bumps it), they can make the post-mint signature check fail on purpose. `pallet-ismp`'s request handler then deletes the request receipt "so it can be timed out," while the mint that already happened is never rolled back — letting the same party both keep the minted destination funds and later collect the source-chain timeout refund.

### Finding Description
`on_accept` performs the transfer/mint to `beneficiary` first: [1](#0-0) 

Only afterwards does it decode and verify the optional calldata's signature, using the beneficiary's current on-chain nonce as part of the signed payload: [2](#0-1) 

If the recovered signer/nonce check fails, `on_accept` returns `Err(HftError::SignatureVerificationFailed)`, but this is thrown *after* the mint/transfer already executed, and nothing rolls that mutation back (`with_transaction`/`#[transactional]` is not used anywhere in the ISMP or HFT pallets). [3](#0-2) 

The caller, `pallet-ismp`'s request handler, treats a failing `on_accept` as "not delivered" and deletes the receipt so the request becomes eligible for a timeout claim, while the overall extrinsic still returns `Ok`, meaning any storage writes performed before the failure (the mint) persist: [4](#0-3) 

This is the same bug class as the report: a party who is the subject of a signature check controls the exact on-chain nonce that check depends on, and can freely desynchronize it to force the check to fail — except here failure isn't just a liquidation block, it flips the request into a refundable/timeoutable state after value has already moved.

### Impact Explanation
Because the beneficiary is typically also the original sender for common "send myself tokens + a follow-up call" flows, or can otherwise coordinate/collude with the sender, this produces an unbacked mint: destination-chain tokens are minted to the beneficiary and are never clawed back, while the source-chain escrow is released to the original sender via the timeout path since the receipt was deleted. This is a direct double-spend of bridged value, a concrete theft/unbacked-mint outcome reachable through the standard token-bridge mint path of `pallet-hyper-fungible-token`.

### Likelihood Explanation
The account nonce is entirely under the beneficiary's control — any ordinary extrinsic they submit between crafting/signing the calldata off-chain and the cross-chain message's arrival bumps it, guaranteeing the signature check fails against the mismatched nonce with no special timing or race required. Any user opting to include calldata (`message.data`) with a signature in an HFT transfer, and who also transacts normally on the destination chain, can trigger this deterministically.

### Recommendation
Do not perform the mint/transfer before validating and successfully dispatching the optional calldata; if calldata is supplied, gate the fund movement on successful calldata verification and dispatch (or wrap the whole `on_accept` body in a transactional storage layer keyed to the calldata's outcome). Additionally, avoid binding externally-triggerable, cross-chain-authorized signatures to a mutable on-chain nonce the signer controls outside of the bridging flow (e.g., use a dedicated bridge-specific nonce/commitment, or the request's own commitment/nonce, instead of `frame_system::account_nonce`).

### Proof of Concept
1. Beneficiary account `B` (equal to or colluding with sender `A`) constructs a cross-chain HFT transfer with `message.data` containing a `SubstrateCalldata` whose signature is computed over `(account_nonce(B), runtime_call)` at nonce `n`.
2. Before the message is relayed and delivered, `B` submits any ordinary extrinsic on the destination chain, incrementing their nonce to `n+1`.
3. The bridged message is delivered; `on_accept` mints/transfers the bridged amount to `B` (lines 93-117), then decodes and checks the signature against `account_nonce(B) == n+1`, which fails verification and returns `Err`.
4. `pallet-ismp`'s `handle()` sees `res.is_err()` and deletes the request receipt, while the overall extrinsic call still succeeds — the mint from step 3 is retained.
5. After the timeout window, anyone submits a timeout message with a non-membership proof of the deleted receipt; `on_timeout` on the source chain refunds the escrowed amount back to `A` (`message.from`).
6. `B`/`A` now holds both the minted destination tokens and the refunded source-chain escrow — an unbacked doubling of the bridged value.

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-140)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L153-171)
```rust
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

**File:** modules/ismp/core/src/handlers/request.rs (L108-126)
```rust
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
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
