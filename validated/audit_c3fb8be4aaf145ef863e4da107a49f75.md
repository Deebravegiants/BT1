Confirmed: both `withdraw_fees` and `accumulate_fees` are `ensure_none` (unsigned, permissionless-submission) extrinsics [1](#0-0) , and both consume the same `Nonce` double-map keyed by `(address, StateMachine)` [2](#0-1) .

### Title
Cross-function signature replay between `withdraw_fees` and `accumulate_fees` due to identical message hash and shared nonce - (File: `modules/pallets/relayer/src/withdrawal.rs`, `modules/pallets/relayer/src/accumulate.rs`)

### Summary
`pallet-ismp-relayer` lets a relayer authorize two semantically different privileged actions — a direct fee withdrawal/payout (`withdraw_fees`) and a beneficiary redirect during fee accumulation (`accumulate_fees`) — with off-chain signatures. Both signed payloads hash the exact same SCALE-encoded tuple `(nonce: u64, StateMachine, beneficiary: Vec<u8>)` and are checked against the exact same `Nonce<T>` counter keyed by `(address, state_machine)`. Because neither message domain-separates the two functions, a signature the relayer produced intending one action can be submitted to the other unsigned entry point instead, since both are `ensure_none` and permissionlessly submittable by anyone who observes the signature.

### Finding Description
`withdrawal.rs::message()` builds the digest signed for `withdraw_fees`: [3](#0-2) 

`accumulate.rs::beneficiary_message()` builds the digest signed for the beneficiary redirect inside `accumulate_fees`: [4](#0-3) 

Both encode `(nonce, StateMachine, beneficiary-bytes)` — SCALE-identical for `Vec<u8>` and `&[u8]` — with no function/action tag, no verifying pallet identifier, and no distinguishing domain separator (unlike the EIP-712-style fix recommended for `ApprovedCallsPolicy`). Both call sites pull the nonce from the *same* storage map:

`withdraw()`: [5](#0-4) 

`accumulate()`: [6](#0-5) 

Both `withdraw_fees` and `accumulate_fees` are unsigned extrinsics (`ensure_none`), dispatchable by anyone who has the encoded call — the pallet's own `validate_unsigned` re-executes the handler during gossip validation, meaning the payload is visible to any node/attacker before/at inclusion: [1](#0-0) [7](#0-6) 

Because the message hash and nonce checkpoint are shared, a signature the relayer created to authorize a beneficiary redirect at `accumulate_fees` time (crediting freshly-proven fees to beneficiary B) is *also* a valid signature for `withdraw_fees` at the same nonce/state machine/beneficiary. An attacker who captures that signature (from the relayer's own submitted/pending `WithdrawalProof.beneficiary_details`, from logs, or from a leaked payload) can front-run it into `withdraw_fees` instead. `withdraw_fees` immediately dispatches an ISMP `WithdrawalParams`/`WithdrawalRequest` disbursing the relayer's *entire currently accumulated* `Fees[dest_chain][address]` balance to beneficiary B and zeroes the balance: [8](#0-7) 

This consumes the nonce, so the relayer's originally-intended `accumulate_fees` call (which would have credited a *specific, smaller, newly-proven* fee amount to B) now fails with a nonce mismatch, and the actually-triggered `withdraw_fees` instead force-drains the *whole* outstanding balance early — an amount, timing, and code path the relayer never explicitly authorized for that signature. Conversely, a signature meant for `withdraw_fees` can be replayed into `accumulate_fees`'s beneficiary field.

### Impact Explanation
This is squarely in-scope "relayer fee and reward accounting." The vulnerability lets a third party redirect *when* and *through which code path* a relayer's already-accrued cross-chain fee balance is disbursed, without the relayer's consent for that specific action — an unauthorized state-mutating action (forced early withdrawal/payout, or DoS/nonce-burn of the intended accumulate call) triggered by replaying a signature across two different privileged functions that share the same signer role, message structure, and nonce counter. This mirrors the reported `ApprovedCallsPolicy` bug class exactly: multiple "policy instances" (here, two pallet dispatchables) sharing one signer/nonce domain and one message-hash schema, enabling replay of an authorization meant for one context into another.

### Likelihood Explanation
Both entry points are unsigned/permissionless (`ensure_none`), so nothing but knowledge of the signature and the ability to submit a transaction is required — an attacker can observe a relayer's `beneficiary_details` signature (public once submitted, or obtainable via mempool/gossip since `validate_unsigned` runs on it) and race a `withdraw_fees` call with the identical fields before the relayer's own `accumulate_fees` call lands. This requires a relayer to actually use the optional `beneficiary_details`/`beneficiary` redirect feature (both are `Option`), so likelihood depends on relayer usage of that path, but no privileged access or governance compromise is needed to exploit it — it only needs one intercepted signature.

### Recommendation
Domain-separate the two message hashes, e.g., include a distinct action tag/selector (and ideally the pallet/call index) in each preimage — `keccak256(("withdraw_fees", nonce, dest_chain, beneficiary))` vs. `keccak256(("accumulate_beneficiary", nonce, state_machine, beneficiary))` — so a signature valid for one function can never satisfy the other, following the same fix pattern (bind the verifying context into the digest) recommended for `ApprovedCallsPolicy`. Alternatively, use disjoint nonce counters per action rather than sharing one `Nonce<T>` map across `withdraw` and `accumulate`.

### Proof of Concept
1. Relayer R has an outstanding `Fees[X][R]` balance and a current `Nonce[R][X] = N`.
2. R signs `beneficiary_message(N, X, B)` intending to submit `accumulate_fees` with `beneficiary_details = Some((B, sig))` to redirect a newly-proven, smaller fee amount to B.
3. Attacker observes `sig` (from the pending/gossiped `accumulate_fees` unsigned extrinsic) and immediately submits `withdraw_fees` with `WithdrawalInputData { signature: sig, dest_chain: X, beneficiary: Some(B) }`.
4. `withdraw()` computes the identical `message(N, X, Some(B))` digest, recovers/validates against the same `sig`, succeeds, increments `Nonce[R][X]` to `N+1`, and dispatches the full current `Fees[X][R]` balance to B, zeroing it out.
5. R's originally intended `accumulate_fees` call, still carrying nonce `N`, now reverts with a nonce mismatch — the relayer's intended, smaller, later redirect never lands, while an unintended full withdrawal already fired via the replayed signature.

### Citations

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

**File:** modules/pallets/relayer/src/lib.rs (L467-491)
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

			if let Err(err) = res {
				log::error!(target: "ismp", "Pallet Relayer Fees error {err:?}");
				Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?
			}

			let encoding = match call {
				Call::accumulate_fees { withdrawal_proof } => withdrawal_proof.encode(),
				Call::withdraw_fees { withdrawal_data } => withdrawal_data.encode(),
				Call::claim_outbound_consensus_delivery_reward { claim } => claim.encode(),
				Call::claim_outbound_request_delivery_reward { claim } => claim.encode(),
				_ => unreachable!(),
			};

```

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

**File:** modules/pallets/relayer/src/withdrawal.rs (L116-187)
```rust
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
			s if s.is_substrate() => (
				HYPERBRIDGE_MODULE_ID.to_vec(),
				Message::WithdrawRelayerFees(WithdrawalRequest {
					amount: available_amount.low_u128(),
					account: AccountId32::try_from(&beneficiary_address[..])
						.map_err(|_| Error::<T>::InvalidPublicKey)?,
				})
				.encode(),
			),
			_ => {
				let HostParam::EvmHostParam(params) =
					HostParams::<T>::get(withdrawal_data.dest_chain)
						.ok_or_else(|| Error::<T>::MissingMangerAddress)?;

				let body = WithdrawalParams {
					beneficiary_address: beneficiary_address.clone(),
					amount: available_amount.into(),
					token: params.fee_token,
				}
				.abi_encode()
				.map_err(|_| Error::<T>::InvalidPublicKey)?;

				(params.host_manager.0.to_vec(), body)
			},
		};

		let post = DispatchPost {
			dest: withdrawal_data.dest_chain,
			from: MODULE_ID.to_vec(),
			to,
			body,
			timeout: 0,
		};

		// Account is not useful in this case
		dispatcher
			.dispatch_request(
				DispatchRequest::Post(post),
				FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() },
			)
			.map_err(|_| Error::<T>::DispatchFailed)?;

		Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero());

		Self::deposit_event(Event::<T>::Withdraw {
			address: sp_runtime::BoundedVec::truncate_from(address.clone()),
			beneficiary_address: sp_runtime::BoundedVec::truncate_from(beneficiary_address),
			state_machine: withdrawal_data.dest_chain,
			amount: available_amount,
		});

		Ok(())
	}
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L192-197)
```rust
pub fn message(nonce: u64, dest_chain: StateMachine, beneficiary: Option<Vec<u8>>) -> [u8; 32] {
	if let Some(beneficiary) = beneficiary {
		return sp_io::hashing::keccak_256(&(nonce, dest_chain, beneficiary).encode());
	}
	sp_io::hashing::keccak_256(&(nonce, dest_chain).encode())
}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L110-126)
```rust
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
