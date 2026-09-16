### Title
Missing function-domain separation lets an `accumulate_fees` beneficiary-redirect signature be replayed to trigger `withdraw_fees` and force an unintended, immediate fee disbursement — ([File: modules/pallets/relayer/src/withdrawal.rs], [File: modules/pallets/relayer/src/accumulate.rs])

### Summary
`pallet-ismp-relayer` signs two structurally different authorizations with byte-identical hash construction and a **shared nonce counter**, keyed by `(address, StateMachine)`. A relayer's EIP-191/raw-key signature intended only to redirect fee *accrual* to a beneficiary inside `accumulate_fees` is bit-for-bit valid input for `withdraw_fees`, which instead dispatches an actual, irreversible on-chain fund transfer. This is the same bug class as the reported KintoID/Faucet issue: the signed payload omits any function-specific domain tag, so a signature meant for one function is accepted by another.

### Finding Description
`withdrawal::message()` hashes `(nonce, dest_chain, beneficiary).encode()` when a beneficiary is present: [1](#0-0) 

`accumulate::beneficiary_message()` hashes `(nonce, state_machine, beneficiary).encode()`: [2](#0-1) 

Both tuples are `(u64, StateMachine, Vec<u8>)` — SCALE-encoding `Vec<u8>` and `&[u8]` produces identical bytes — so for the same `(nonce, chain, beneficiary)` triple the two functions compute the **exact same keccak256 digest**. Neither hash includes a function selector, call-index, or any other domain separator distinguishing "authorize a beneficiary redirect at accumulate-time" from "authorize an immediate withdrawal."

Compounding this, both call sites read and increment the **same** `Nonce<T>` storage double-map keyed by `(address, StateMachine)`: [3](#0-2) [4](#0-3) 

Both `accumulate_fees` and `withdraw_fees` are permissionless (`ensure_none`) unsigned extrinsics that any party can submit with attacker-supplied call data, and both are dispatched through the same `validate_unsigned` path: [5](#0-4) [6](#0-5) 

Consequently, once a relayer produces a signature `S` over `(nonce=N, chain=X, beneficiary=B)` for use with `accumulate_fees` (a low-consequence bookkeeping redirect for future fee attribution), that same `S` is a valid signature for a `WithdrawalInputData{ signature: S, dest_chain: X, beneficiary: Some(B) }` submitted to `withdraw_fees`, as long as the shared nonce for `(address, X)` is still `N`.

### Impact Explanation
An unprivileged third party who observes `S` (e.g. from mempool, a previous transaction, or any off-chain channel the relayer used) can front-run the relayer's intended `accumulate_fees` call by submitting `withdraw_fees` with the same `(S, X, B)`. Since `withdraw_fees`:
- verifies the signature against the identical hash and succeeds,
- reads `Fees::<T>::get(X, address)` and dispatches an ISMP POST moving the relayer's **entire currently accrued `available_amount`** to beneficiary `B`,
- zeroes `Fees` and increments the shared nonce,

this converts a signature that only authorized a bookkeeping redirect into an actual, irreversible on-chain fund disbursement the relayer never explicitly authorized at that time. It also burns the shared nonce, so the relayer's originally-intended `accumulate_fees` call (still carrying nonce `N`) subsequently fails signature/nonce checks, denying the relayer the intended beneficiary-redirect action and forcing them to re-sign. This is an unauthorized state transition (forced fund movement) triggered by cross-function signature reuse — the same root cause identified in the external KintoID/Faucet report — reachable by any unprivileged relayer-flow participant, hence Medium severity (funds still land at the relayer-chosen beneficiary, so it is not outright theft, but it forces premature/unauthorized withdrawal and desynchronizes/DoSes the relayer's intended call).

### Likelihood Explanation
Both extrinsics are unsigned and permissionless, requiring no special role — any address able to observe a relayer's signature (which must be produced and possibly shared/broadcast to be submitted via either flow) can immediately reuse it against the other function as long as the nonce hasn't advanced. No additional access or privilege is required, only routine monitoring of pending relayer fee-management transactions.

### Recommendation
Include a function-specific domain separator (e.g., the call index / a `b"WITHDRAW"` vs `b"ACCUMULATE_BENEFICIARY"` tag) inside both `message()` and `beneficiary_message()` before hashing, so the two authorizations can never collide. Additionally, consider using independent nonce namespaces (or including a purpose tag in the nonce key) for the two flows so that consuming one signature's nonce cannot invalidate or be conflated with the other's.

### Proof of Concept
1. Relayer `R` signs `S = sign(keccak256((N, X, B).encode()))` intending to submit `accumulate_fees` with `beneficiary_details = Some((B, S))` for state machine `X` at nonce `N` (`Nonce[R, X] == N`).
2. Before `R`'s `accumulate_fees` extrinsic lands, an attacker observes `(S, X, B)` and submits `withdraw_fees` with `WithdrawalInputData{ signature: S (as Evm{address:R,...}), dest_chain: X, beneficiary: Some(B) }`.
3. `Pallet::withdraw` computes `msg = message(N, X, Some(B))`, which equals `beneficiary_message(N, X, B)` byte-for-byte; `signature.verify(&msg, None)` recovers `R`, matching `address`.
4. `withdraw` succeeds: it reads `Fees[X][R]`, dispatches an ISMP POST transferring the full accrued amount to `B`, zeroes `Fees[X][R]`, and bumps `Nonce[R, X]` to `N+1`.
5. `R`'s subsequently submitted `accumulate_fees` call, still built against nonce `N`, now fails (`Nonce[R,X] != N`), and the relayer's intended fee-accrual redirect never executes despite `R`'s pending unclaimed fee commitments being in flight.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L81-99)
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

**File:** modules/pallets/relayer/src/lib.rs (L350-368)
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

		#[pallet::call_index(1)]
		#[pallet::weight({1_000_000})]
		pub fn withdraw_fees(
			origin: OriginFor<T>,
			withdrawal_data: WithdrawalInputData,
		) -> DispatchResult {
			ensure_none(origin)?;
			Self::withdraw(withdrawal_data)
		}
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
