Confirmed: `Nonce<T>` is a single `StorageDoubleMap<AccountBytes, StateMachine, u64>` shared by both `withdrawal::withdraw` and `accumulate::accumulate`, and both call sites hash an identical `(u64, StateMachine, Vec<u8>)` tuple with no domain/method tag to bind the signature to a specific extrinsic.

### Title
Cross-function signature replay via identical unsigned-payload hash construction in `pallet-ismp-relayer` beneficiary messages - (File: `modules/pallets/relayer/src/withdrawal.rs`, `modules/pallets/relayer/src/accumulate.rs`)

### Summary
`pallet-ismp-relayer` signs two structurally distinct, security-critical redirect authorizations — the withdrawal beneficiary in `withdraw()` and the fee-accumulation beneficiary in `accumulate()` — with the exact same message construction: `keccak256(SCALE_encode(nonce: u64, state_machine: StateMachine, beneficiary: Vec<u8>))`. Neither payload embeds a method/action discriminator, so the two functions are unable to distinguish a signature intended for one from a signature intended for the other. This is the same class of defect flagged in the referenced Muon `LibMuon` report: hashing scheme reused across multiple distinct verification contexts without a method tag.

### Finding Description
`withdrawal::message` in [1](#0-0)  computes `keccak256((nonce, dest_chain, beneficiary).encode())` when a beneficiary is supplied, which is verified in `Pallet::withdraw` at [2](#0-1) , keyed off the shared `Nonce::<T>::get(address, dest_chain)`.

`accumulate::beneficiary_message` in [3](#0-2)  computes `keccak256((nonce, state_machine, beneficiary).encode())` — the identical field types in the identical order — verified in `Pallet::accumulate` at [4](#0-3) , keyed off the same `Nonce::<T>::get(&delivery_address, state_machine)` storage item.

Both call sites read/increment the same `Nonce<T>` double map defined once for the whole pallet: [5](#0-4) . Since `u64` and `StateMachine` SCALE-encode identically regardless of call site, and `beneficiary`/`Vec<u8>` encode the same length-prefixed bytes in both, for a given relayer address and destination state machine at a given nonce value, `message(nonce, dest_chain, Some(beneficiary))` and `beneficiary_message(nonce, dest_chain, &beneficiary)` produce byte-for-byte identical digests. A relayer's signature authorizing one action (e.g., redirecting a `withdraw_fees` payout) is therefore also a valid signature for the unrelated `accumulate_fees` beneficiary redirect (or vice versa) at the same nonce/state-machine/beneficiary triple, because nothing in the signed payload identifies which extrinsic/method it authorizes.

### Impact Explanation
An attacker who observes or is handed a relayer's beneficiary-redirect signature intended for one extrinsic (`withdraw_fees` or `accumulate_fees`) can submit it against the other extrinsic, since both are unsigned/`ensure_none` calls dispatchable by any unprivileged submitter (see `validate_unsigned` at [6](#0-5) ). This can redirect a relayer's accrued fee payout to an unintended beneficiary at the colliding nonce, misdirecting or freezing relayer reward funds, and undermines the guarantee that a signature only authorizes the specific action the relayer intended.

### Likelihood Explanation
Both extrinsics are permissionless/unsigned, dispatchable by any address once a valid signature+nonce+beneficiary triple is known: an attacker only needs to intercept a signature that a relayer produced for one flow (e.g., from a mempool, a public claim UI, or another relayer's published tx) and resubmit it against the sibling extrinsic while the nonce is still valid. No special privileges or chain compromise are required — this matches the audit report's "Medium" severity classification for hash-collision-enabled signature abuse.

### Recommendation
Include a method/action discriminator (e.g., a fixed byte tag or the call's `Call::method` name) inside the hashed payload of both `withdrawal::message` and `accumulate::beneficiary_message`, so a signature produced for one extrinsic can never be replayed as valid input to the other. Apply this fix consistently to every relayer-signed payload in this pallet — `withdrawal::message`, `accumulate::beneficiary_message`, `outbound_consensus::outbound_consensus_delivery_message`, and `outbound_request::outbound_request_delivery_message` — rather than patching only the two shown here to colide, mirroring the audit's recommendation to apply the fix to *all* affected functions, not a selected few.

### Proof of Concept
1. Relayer R delivers requests to destination `D` and has `Nonce::<T>::get(R, D) == n`.
2. R signs `withdrawal::message(n, D, Some(B))` to redirect a `withdraw_fees` payout to beneficiary `B`, intending to submit `withdraw_fees` with this signature.
3. Attacker intercepts this signature before/instead of it landing, and instead submits `accumulate_fees` with a `WithdrawalProof.beneficiary_details = Some((B, signature))`, using the same `nonce = n` and `state_machine = D`.
4. `Pallet::accumulate` computes `beneficiary_message(n, D, B)` — byte-identical to `withdrawal::message(n, D, Some(B))` — and `signature.verify(&msg, ...)` succeeds because the digest matches, redirecting R's accumulated fee to `B` via the `accumulate_fees` path R never authorized for that purpose.
5. `Nonce::<T>` is bumped by whichever call lands, invalidating R's intended follow-up call and confirming the two entry points share replayable authorization state.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L88-96)
```rust
		let nonce = Nonce::<T>::get(address.clone(), withdrawal_data.dest_chain);
		let msg = message(nonce, withdrawal_data.dest_chain, withdrawal_data.beneficiary.clone());

		match &withdrawal_data.signature {
			Signature::Evm { address, .. } => {
				let eth_address = withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L190-197)
```rust
/// Signed payload for [`WithdrawalInputData`]. Includes the per-relayer nonce so a captured
/// signature cannot be replayed.
pub fn message(nonce: u64, dest_chain: StateMachine, beneficiary: Option<Vec<u8>>) -> [u8; 32] {
	if let Some(beneficiary) = beneficiary {
		return sp_io::hashing::keccak_256(&(nonce, dest_chain, beneficiary).encode());
	}
	sp_io::hashing::keccak_256(&(nonce, dest_chain).encode())
}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L107-126)
```rust
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

**File:** modules/pallets/relayer/src/lib.rs (L124-135)
```rust
	/// Latest nonce for each address and the state machine they want to withdraw from
	#[pallet::storage]
	#[pallet::getter(fn nonce)]
	pub type Nonce<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		Vec<u8>,
		Blake2_128Concat,
		StateMachine,
		u64,
		ValueQuery,
	>;
```

**File:** modules/pallets/relayer/src/lib.rs (L467-477)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let res = match call {
				Call::accumulate_fees { withdrawal_proof } =>
					Self::accumulate(withdrawal_proof.clone()),
				Call::withdraw_fees { withdrawal_data } => Self::withdraw(withdrawal_data.clone()),
				Call::claim_outbound_consensus_delivery_reward { claim } =>
					Self::process_outbound_consensus_delivery_claim(claim.clone()),
				Call::claim_outbound_request_delivery_reward { claim } =>
					Self::process_outbound_request_delivery_claim(claim.clone()),
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};
```
