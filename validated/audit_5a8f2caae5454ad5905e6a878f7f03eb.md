### Title
Unvalidated `beneficiary_address` in relayer fee redirect permanently locks accumulated fees - (File: `modules/pallets/relayer/src/accumulate.rs`)

### Summary
`pallet_ismp_relayer::accumulate` lets the caller of the permissionless (`ensure_none`) `accumulate_fees` extrinsic redirect the delivery relayer's earned fee to an arbitrary `beneficiary_address` byte-string, without ever checking that this address is a well-formed, chain-appropriate account (20 bytes for EVM, a valid public key for Substrate) for the destination `state_machine`. This mirrors the reported bug class — writing a mapping value keyed by an address that was never validated to exist/be well-formed — except here the mapping is the relayer's `Fees` balance, and the consequence is permanent loss of access to the credited funds rather than a harmless no-op write.

### Finding Description
In `Pallet::<T>::accumulate` [1](#0-0) , when `withdrawal_proof.beneficiary_details` is `Some((beneficiary_address, signature))`, the code:
1. Verifies the signature was produced by the private key of `delivery_address` (the relayer who actually delivered the message), over a message that only binds `nonce`, `state_machine`, and `beneficiary_address` bytes.
2. Never inspects `beneficiary_address` itself — no length check, no check that it decodes to a valid 20-byte `H160` for EVM destinations or a valid public key for Substrate destinations.
3. Credits the fee directly into `Fees::<T>::try_mutate(state_machine, beneficiary_address.clone(), |inner| *inner += total_fee)` [2](#0-1) .

Later, funds stored under a `Fees` key can only be reached through `Pallet::<T>::withdraw` [3](#0-2) , whose `address` used to index `Fees::<T>::get(dest_chain, address)` is *recovered from an ECDSA/sr25519/ed25519 signature* supplied by the caller — i.e., it is always a canonically-derived, correctly-sized address (20 bytes for `Signature::Evm`, or a valid public key otherwise). If `beneficiary_address` recorded during `accumulate` is not itself a byte string that can ever be produced as a signature-recovery result (wrong length, arbitrary/garbage bytes, or a value that happens not to correspond to any keypair the beneficiary controls), no future call to `withdraw` can ever match that key, and the `Fees` entry becomes permanently unreachable.

This is the same root defect as the referenced report: a value is written into a mapping under a key without validating that the key corresponds to a real, addressable entity — except the consequence here is concrete: funds credited to that mapping key can never be withdrawn.

### Impact Explanation
This causes **permanent freezing of funds** — relayer fees legitimately earned for delivering cross-chain messages become permanently locked in on-chain storage once redirected to a malformed `beneficiary_address`, with no recovery path (there is no admin function to correct or reassign a `Fees` entry). Because relayer reward accounting is explicitly an in-scope Hyperbridge asset-affecting surface, and the loss is total and irreversible for the affected amount, this qualifies as at least Medium severity.

### Likelihood Explanation
`accumulate_fees` is dispatched with `ensure_none` origin [4](#0-3)  — it is permissionless and reachable by any party submitting a valid `WithdrawalProof`, including the optional `beneficiary_details`. The only party who can trigger the vulnerable path is whoever holds `delivery_address`'s private key (since the signature must recover to `delivery_address`), which limits it mostly to the relayer redirecting its own reward — but that redirect is a normal operational feature (e.g. tesseract relayer clients redirecting rewards to a treasury/hot-wallet address), and a bug or misconfiguration in the byte-encoding of that address (off-by-one truncation, wrong endianness, wrong address type for the destination chain family) silently and irrecoverably destroys the relayer's fee balance. No validation exists to catch such a mistake before the credit is made.

### Recommendation
Before crediting `Fees[state_machine][beneficiary_address]`, validate that `beneficiary_address` is well-formed for the destination chain's address family — exactly 20 bytes and non-zero for `state_machine.is_evm()`, or a valid 32-byte public key for substrate destinations — and reject the extrinsic with a new `Error::<T>::InvalidBeneficiaryAddress` (mirroring the existing check already present for `WithdrawalParams` in `pallet-host-executive` [5](#0-4) ) if it is not.

### Proof of Concept
1. A relayer delivers a batch of messages and is entitled to fees under `delivery_address`.
2. It (or tooling acting on its behalf) calls `accumulate_fees` with `beneficiary_details = Some((malformed_bytes, signature))`, where `signature` correctly proves `delivery_address` authorized the redirect, but `malformed_bytes` is not a valid EVM/substrate address (e.g., 19 bytes, or 20 bytes that do not correspond to any recoverable ECDSA public key format expected downstream).
3. `Fees::<T>::try_mutate(state_machine, malformed_bytes, |inner| *inner += total_fee)` succeeds and credits the fee [2](#0-1) .
4. No account can ever produce a `WithdrawalInputData::signature` that recovers to `malformed_bytes` in `Pallet::<T>::withdraw` [6](#0-5) , so `Fees::<T>::get(dest_chain, malformed_bytes)` is permanently inaccessible — the credited fee is frozen forever.

Note: I was unable to fully trace whether any Hyperbridge SDK/tesseract client-side validation currently prevents a malformed `beneficiary_address` from being submitted in practice; the pallet itself performs no such check, which is the root cause identified above.

### Citations

**File:** modules/pallets/relayer/src/accumulate.rs (L106-147)
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
		} else {
			let _ = Fees::<T>::try_mutate(state_machine, delivery_address.clone(), |inner| {
				*inner += total_fee;
				Ok::<(), ()>(())
			});

			delivery_address
		};
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L81-134)
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

		let dispatcher = <T as Config>::IsmpHost::default();

		Nonce::<T>::try_mutate(address.clone(), withdrawal_data.dest_chain, |value| {
			*value += 1;
			Ok::<(), ()>(())
		})
		.map_err(|_| Error::<T>::ErrorCompletingCall)?;

		let beneficiary_address = withdrawal_data.beneficiary.clone().unwrap_or(address.clone());
		let (to, body) = match withdrawal_data.dest_chain {
```

**File:** modules/pallets/relayer/src/lib.rs (L350-358)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight({1_000_000})]
		pub fn accumulate_fees(
			origin: OriginFor<T>,
			withdrawal_proof: WithdrawalProof,
		) -> DispatchResult {
			ensure_none(origin)?;
			Self::accumulate(withdrawal_proof)
		}
```

**File:** modules/pallets/host-executive/src/lib.rs (L164-165)
```rust
		/// The beneficiary address in `WithdrawalParams` was not a valid 20-byte EVM address
		InvalidBeneficiaryAddress,
```
