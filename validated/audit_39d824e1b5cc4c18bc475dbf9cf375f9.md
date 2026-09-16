### Title
Relayer fees redirected to a signature-incapable "beneficiary" address (e.g. a smart contract) become permanently unclaimable - (File: modules/pallets/relayer/src/withdrawal.rs)

### Summary
`pallet-relayer`'s `accumulate_fees` extrinsic lets the delivering relayer redirect its earned fee credit to an arbitrary `beneficiary_address` (any byte string, no format/ownership validation) by supplying its own signature over the redirect message. The credited fee balance can only later be withdrawn via `withdraw_fees`, which requires a signature *from the beneficiary itself* that cryptographically recovers to that same address. If the chosen `beneficiary_address` is a smart-contract address (or any address with no corresponding private key), no such signature can ever be produced, and the accumulated fee balance is permanently frozen — the same root cause as Sherlock M-18, where a royalty `claimRoyalties()`-style function gates payout on an address that may be incapable of authenticating the claim.

### Finding Description
In `modules/pallets/relayer/src/accumulate.rs`, when a `WithdrawalProof` includes `beneficiary_details: Some((beneficiary_address, signature))`, the pallet verifies the **delivering relayer's** signature over `beneficiary_message(nonce, state_machine, &beneficiary_address)` — proving only that the relayer who delivered the message authorized the redirect — and then credits the fee straight to `beneficiary_address` with no constraint on what that address is: [1](#0-0) 

`beneficiary_address` is accepted as an arbitrary `Vec<u8>` and stored as the `Fees` map key: [2](#0-1) 

Later, to actually move funds out, `withdraw_fees` requires a signature whose recovered/verified signer **must equal** the account holding the balance: [3](#0-2) 

The `address` used to look up and zero the `Fees` balance is derived exclusively from the signature (`Signature::Evm` → ECDSA-recovered address, `Signature::Sr25519`/`Ed25519` → the signer's public key). There is no code path that allows a third party, a contract's admin, or anyone else to withdraw on behalf of `beneficiary_address` if that address does not correspond to a private key an off-chain party controls (e.g., an EVM smart-contract address, a precompile address, or any account with no keypair).

This is structurally identical to the Sherlock M-18 root cause: `InfernalRiftAbove::claimRoyalties()` gates the payout on `msg.sender == receiver`, where `receiver` is set by external logic (ERC-2981 `royaltyInfo`) that can be a contract unable to originate the call. Here, `beneficiary_address` is likewise set by an operation the ultimate payee does not control (the relayer's redirect), and the payout is gated on the payee producing a private-key signature that a smart-contract address structurally cannot produce.

### Impact Explanation
Any fee balance credited under a `beneficiary_address` lacking a private key is permanently and irrecoverably frozen in the `Fees` storage map — there is no admin override, no anyone-can-withdraw-after-timeout fallback, and no alternate redemption path (unlike the intents cancellation flow, which has a public fallback after expiry). Given that relayer fee accounting directly represents real economic value owed to relayers/operators, and the freeze is total and permanent for the affected balance, this constitutes a genuine freezing-of-funds bug.

### Likelihood Explanation
The `beneficiary_address` is supplied off-chain as part of `WithdrawalProof.beneficiary_details` by whichever relayer submits the `accumulate_fees` proof — an unprivileged, permissionless extrinsic (`ensure_none(origin)`). A relayer operator could misconfigure its beneficiary (e.g., point fee accrual at a treasury/vault contract expecting it to later "claim" funds the way a normal wallet would), or an attacker with delivery-key access could deliberately redirect a victim relayer's fee credit to an unclaimable address purely to grief. No consensus proof forgery or governance action is required — only a valid delivery signature the relayer already possesses.

### Recommendation
- Require `withdraw_fees` (or a companion extrinsic) to support delegated/permissionless withdrawal to a fixed `beneficiary_address` once it has been set via `accumulate_fees`, so redemption does not depend on the beneficiary being able to produce a fresh signature.
- Alternatively, validate at `accumulate_fees` time that `beneficiary_address` corresponds to a format/derivation that guarantees a controllable keypair, and/or allow the original `delivery_address` (which did sign) to reclaim/redirect funds if the beneficiary proves unable to withdraw within a timeout.
- Emit and document the risk clearly so relayer tooling never accepts a beneficiary address without an accompanying signature capability check.

### Proof of Concept
1. Relayer `R` (holding an EVM keypair) delivers a message and becomes eligible to accumulate a fee via `accumulate_fees`.
2. `R` submits the proof with `beneficiary_details = Some((beneficiary_bytes, R's signature over beneficiary_message(nonce, dest_chain, beneficiary_bytes)))`, where `beneficiary_bytes` is an arbitrary 20-byte value equal to the address of a smart contract on the destination chain (no corresponding private key exists).
3. `accumulate` in `accumulate.rs` verifies `R`'s signature (recovering to `R`, matching `delivery_address`), then credits `Fees::<T>::get(state_machine, beneficiary_bytes)` with `total_fee`. See `modules/pallets/relayer/src/accumulate.rs` lines 106–139.
4. No account controls the private key for `beneficiary_bytes`; `withdraw_fees` (`modules/pallets/relayer/src/withdrawal.rs` lines 81–99) can never be called with a signature that verifies to `beneficiary_bytes`.
5. The credited `Fees` balance under `(state_machine, beneficiary_bytes)` remains permanently unclaimable.

### Citations

**File:** modules/pallets/relayer/src/accumulate.rs (L106-139)
```rust
		// Let's verify the beneficiary address
		let beneficiary_address = if let Some((beneficiary_address, signature)) =
			withdrawal_proof.beneficiary_details
		{
			let nonce = Nonce::<T>::get(&delivery_address, state_machine);
			let msg = beneficiary_message(nonce, state_machine, &beneficiary_address);
			match &signature {
				Signature::Evm { .. } => {
					let eth_address =
						signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
					if eth_address != delivery_address {
						Err(Error::<T>::InvalidPublicKey)?
					}
				},
				Signature::Sr25519 { .. } | Signature::Ed25519 { .. } => {
					// verify the signature with the delivery address from the state proof
					let _ = signature
						.verify(&msg, Some(delivery_address.clone()))
						.map_err(|_| Error::<T>::InvalidSignature)?;
				},
			}

			Nonce::<T>::try_mutate(&delivery_address, state_machine, |value| {
				*value += 1;
				Ok::<(), ()>(())
			})
			.map_err(|_: ()| Error::<T>::ErrorCompletingCall)?;

			let _ = Fees::<T>::try_mutate(state_machine, beneficiary_address.clone(), |inner| {
				*inner += total_fee;
				Ok::<(), ()>(())
			});

			beneficiary_address
```

**File:** modules/pallets/relayer/src/accumulate.rs (L303-315)
```rust
}

/// Signed payload authorising a beneficiary redirect on a specific source chain.
/// Including the relayer nonce alongside the state machine keeps the signature usable for
/// exactly one accumulate call on that chain, mirroring how `withdraw_fees` binds its signed
/// payload.
pub fn beneficiary_message(
	nonce: u64,
	state_machine: StateMachine,
	beneficiary: &[u8],
) -> [u8; 32] {
	sp_io::hashing::keccak_256(&(nonce, state_machine, beneficiary).encode())
}
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L81-123)
```rust
	pub fn withdraw(withdrawal_data: WithdrawalInputData) -> DispatchResult {
		let address = match &withdrawal_data.signature {
			Signature::Evm { address, .. } => address.clone(),
			Signature::Sr25519 { public_key, .. } => public_key.clone(),
			Signature::Ed25519 { public_key, .. } => public_key.clone(),
		};

		let nonce = Nonce::<T>::get(address.clone(), withdrawal_data.dest_chain);
		let msg = message(nonce, withdrawal_data.dest_chain, withdrawal_data.beneficiary.clone());

		match &withdrawal_data.signature {
			Signature::Evm { address, .. } => {
				let eth_address = withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
				if &eth_address != address {
					Err(Error::<T>::InvalidPublicKey)?
				}
			},
			Signature::Sr25519 { .. } => {
				// Verify signature with public key provided in signature enum
				withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
			},
			Signature::Ed25519 { .. } => {
				// Verify signature with public key provided in signature enum
				withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
			},
		};
		let available_amount = Fees::<T>::get(withdrawal_data.dest_chain, address.clone());

		if available_amount <
			Self::min_withdrawal_amount(withdrawal_data.dest_chain)
				.unwrap_or(MinWithdrawal::get())
		{
			Err(Error::<T>::NotEnoughBalance)?
		}
```
