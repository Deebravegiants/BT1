## Finding [1](#0-0) [2](#0-1) 

### Title
Relayer can invalidate its own signed fee-beneficiary-redirect commitment by front-running with an unrelated nonce-consuming action, sharing a single `Nonce` map across two independent signed-message flows - ([File: modules/pallets/relayer/src/withdrawal.rs])

### Summary
`pallet-relayer` uses a single per-`(address, dest_chain)` counter, `Nonce<T>`, to bind two structurally different off-chain-signed messages: the plain fee `withdraw_fees` message (`withdrawal.rs::message`) and the fee-redirect `beneficiary_details` signature verified inside `accumulate_fees` (`accumulate.rs::beneficiary_message`). Both code paths read the *current* `Nonce<T>::get(address, chain)`, verify a signature over a payload embedding that nonce, and only bump the nonce after successful verification.

### Finding Description
`Pallet::withdraw` reads `Nonce::<T>::get(address.clone(), withdrawal_data.dest_chain)`, builds `message(nonce, dest_chain, beneficiary)`, verifies the relayer's signature against it, and on success does `Nonce::<T>::try_mutate(..., |value| *value += 1 ...)` [3](#0-2) .

Independently, inside `Pallet::accumulate`, when a delivering relayer attaches `beneficiary_details` to redirect the fee payout to a different address, the code reads `Nonce::<T>::get(&delivery_address, state_machine)`, builds `beneficiary_message(nonce, state_machine, beneficiary)`, verifies the signature, and on success bumps the *same* `Nonce<T>` entry for `(delivery_address, state_machine)` [2](#0-1) .

Because both flows consume the exact same nonce slot for the exact same `(address, chain)` key, a relayer who has already produced an off-chain `beneficiary_message` signature (nonce N) — for example handed to a counterparty or service that expects to be paid via a fee-redirect — can unilaterally invalidate that commitment at will, without any race condition even needed: simply call `withdraw_fees` (or another `accumulate_fees` redirect) for the same `(address, chain)` pair first. That call succeeds under nonce N, bumps the counter to N+1, and the previously issued `beneficiary_message` signature (still bound to N) permanently fails `InvalidSignature`/`InvalidPublicKey` verification when it is later submitted — this is the same underlying bug class as the referenced report: a shared, unrelated-action-incrementable nonce used inside a signature-verification hash lets the signer unilaterally revoke a commitment before it lands on-chain.

Unlike the original Symmetrical report (which needed a mempool race), here the signer holds the private key for both nonce-consuming paths and can deterministically pre-empt the redirect by simply submitting any valid self-signed action first — no front-running timing is even required, only sequencing.

### Impact Explanation
A relayer that has cryptographically committed (off-chain) to redirecting its earned Hyperbridge fees to a beneficiary (e.g., a service split, an escrow agreement, or a downstream payout obligation) can renege on that commitment at will by bumping its own `Nonce<T>` via an unrelated `withdraw_fees` call, permanently invalidating the beneficiary-redirect signature before anyone submits `accumulate_fees` with it. The fees remain entirely under the signer's control instead of moving to the party the signed commitment promised them to, which is a concrete diversion/loss of funds for the intended beneficiary of a validly-signed message. This is a Medium/High severity issue within the relayer fee and reward accounting surface explicitly in scope.

### Likelihood Explanation
Reachable by any unprivileged relayer that has accrued fees and previously produced a `beneficiary_message` signature — a normal, permissionless operation. No special privileges, timing races, or third-party cooperation are required; the signer alone can invalidate their own prior commitment deterministically by issuing one ordinary `withdraw_fees` extrinsic before the counterparty submits the `accumulate_fees` proof carrying the beneficiary redirect.

### Recommendation
Separate the nonce namespaces used by `withdraw_fees` and by the `beneficiary_details` redirect inside `accumulate_fees` (e.g., distinct storage maps, or a nonce/purpose tag baked into the signed payload), so that consuming one intent cannot invalidate the other. Alternatively, bind the beneficiary-redirect signature to a value that cannot be altered by an unrelated call on the same account (e.g., the specific commitment/batch being claimed) rather than to a globally shared, easily-bumped per-chain nonce.

### Proof of Concept
1. Relayer `R` accrues fees on chain `C` for delivering requests, tracked in `Fees::<T>[C, R]`, with `Nonce::<T>[R, C] == N`.
2. `R` signs `beneficiary_message(N, C, B)` off-chain, handing this signature to counterparty `B` (or a service) who will later submit it inside an `accumulate_fees(WithdrawalProof { beneficiary_details: Some((B, sig)), .. })` extrinsic once it has assembled the delivery/state proofs.
3. Before `B`'s `accumulate_fees` lands, `R` submits `withdraw_fees(WithdrawalInputData { signature: sign(message(N, C', None)), dest_chain: C', .. })` for any chain (including `C`), which passes signature verification against `message(N, ...)` and bumps `Nonce::<T>[R, C]` to `N+1` via `withdrawal.rs` [4](#0-3) .
4. `B`'s later `accumulate_fees` call re-derives `Nonce::<T>::get(R, C) == N+1`, recomputes `beneficiary_message(N+1, C, B)`, which does not match the previously-signed message for `N`, so `signature.verify(&msg, ...)` fails with `Error::<T>::InvalidSignature` [5](#0-4) .
5. `R` retains full control of `Fees::<T>[C, R]` and can withdraw it entirely for itself, while `B` never receives the fee share it was cryptographically promised.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L81-131)
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
```

**File:** modules/pallets/relayer/src/accumulate.rs (L106-132)
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
```
