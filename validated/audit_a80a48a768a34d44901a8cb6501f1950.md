### Title
Unbounded `WithdrawalProof.commitments` in `pallet_ismp_relayer::accumulate_fees` allows DoS of relayer fee accrual - (File: modules/pallets/relayer/src/accumulate.rs)

### Summary
The `accumulate_fees` extrinsic is an unsigned call (`ensure_none(origin)`), reachable by any relayer/anyone submitting an unsigned transaction, that runs `Pallet::accumulate` over a caller-supplied `WithdrawalProof { commitments: Vec<H256>, .. }` with no bound on the length of `commitments`. Every stage of `accumulate` — deduplication, filtering against `RequestCommitments`, storage-key derivation, state-proof verification, and result validation — iterates the full `commitments` vector, and the extrinsic is charged a flat, non-scaling weight (`#[pallet::weight({1_000_000})]`). This mirrors the Sherlock finding in Carapace's `ProtectionPool`, where an unbounded array iterated inside a premium-accrual function could grow large enough to exceed gas/weight limits and break the accrual path.

### Finding Description
`accumulate_fees` dispatches directly into `Pallet::<T>::accumulate`: [1](#0-0) 

`accumulate` accepts a `WithdrawalProof` whose `commitments` field is a plain `Vec<H256>` with no `BoundedVec`/length cap: [2](#0-1) 

Inside `accumulate`, the commitments vector is iterated multiple times in sequence — for de-duplication, for filtering against on-chain state, and then used to derive keys and verify state proofs: [3](#0-2) 

`source_fee_commitment_keys` and `receipts_state_trie_key`/`verify_state_proof`/`validate_results` all perform per-commitment work (key derivation, decoding, signature/receipt decoding) proportional to the size of the caller-supplied vector: [4](#0-3) [5](#0-4) 

Despite this per-item work scaling with input size, the extrinsic's declared weight is a constant: [6](#0-5) 

Because the call is dispatched via `ensure_none` (unsigned), an attacker does not need to hold funds or a valid relayer identity to submit a call — they only need a syntactically-valid `WithdrawalProof` (the proof-verification failure happens only after the up-front iteration/filtering work has run). Repeatedly submitting maximal-size commitment vectors forces the runtime to spend far more execution time per block than the fixed weight accounts for, which can push actual execution past the block's real budget while the scheduler continues to admit these calls at their declared (cheap) weight — a classic DoS-via-unbounded-loop pattern, directly analogous to the reported `activeProtectionIndexes` growth in `ProtectionPool._accruePremiumAndExpireProtections`.

### Impact Explanation
If the per-call weight is mis-accounted relative to actual computation (RLP/SCALE decoding, signature verification helpers, and trie-key derivation per commitment), an attacker can craft large-but-cheap-to-produce vectors of `H256` commitments (they don't need to be valid delivered requests — the filter/lookups just skip invalid ones after doing the work) to consume disproportionate block execution time relative to the fee charged, degrading or halting legitimate relayer fee accrual (`accumulate_fees`) and, in a severe enough case, other transactions sharing the block. This directly threatens the "route unable to deliver messages"/reward-accounting availability guarantee described in the validation criteria, since relayers depend on `accumulate_fees` to be reliably processable to receive delivery rewards.

### Likelihood Explanation
Medium: the call is unsigned and requires no token custody, and the vector length is entirely attacker-controlled with no on-chain bound. However, the call still must pass `validate_unsigned`/txpool inclusion rules and ultimately fails proof verification for garbage commitments, meaning the attacker pays no fee but the constant weight charge for the call may already reflect an assumption of a small commitments batch — the actual severity depends on whether the flat `1_000_000` weight is enforced as a hard per-block admission cost cap that meaningfully bounds vector size in practice (this could not be fully confirmed from the available context, e.g., whether `ValidateUnsigned::pre_dispatch`/transaction-pool size limits or extrinsic length limits already constrain `commitments.len()` indirectly through encoded call size).

### Recommendation
- Change `WithdrawalProof.commitments` to a `BoundedVec<H256, MaxCommitmentsPerBatch>` with an explicit, small cap (e.g., matching the relayer's fee-claim chunking `keys.chunks(50)` already used off-chain in `tesseract/messaging/fees/src/lib.rs`).
- Make the declared `#[pallet::weight(...)]` for `accumulate_fees` scale with `commitments.len()` (e.g. `WeightInfo::accumulate_fees(len)`), rather than being a flat constant, so the runtime's weight accounting matches real per-commitment work.
- Reject batches whose length exceeds the bound in `validate_unsigned`/`pre_dispatch`, before any storage lookups or state-proof verification.

### Proof of Concept
1. Craft a `WithdrawalProof` with `commitments` containing, e.g., tens of thousands of arbitrary `H256` values (they need not correspond to real requests).
2. Submit it via the unsigned `accumulate_fees` call repeatedly.
3. Each call runs: `BTreeSet` dedup over all commitments, a `RequestCommitments::get` storage read per commitment (all miss, filtered out), and (if commitments do exist) additional key-derivation/decoding work per surviving item — yet is charged the flat `1_000_000` weight declared in `#[pallet::weight({1_000_000})]` in `modules/pallets/relayer/src/lib.rs:361`.
4. Because cost scales with `commitments.len()` while the declared weight does not, repeated submissions can consume execution time disproportionate to the weight budgeted, degrading block processing for legitimate `accumulate_fees` calls and other extrinsics in the same block — the same DoS pattern flagged in the source Carapace report for `_accruePremiumAndExpireProtections`'s unbounded `activeProtectionIndexes` loop.

### Citations

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

**File:** modules/pallets/relayer/src/lib.rs (L360-358)
```rust

```

**File:** modules/pallets/relayer/src/withdrawal.rs (L48-61)
```rust
#[derive(
	Debug, Clone, Encode, Decode, DecodeWithMemTracking, scale_info::TypeInfo, PartialEq, Eq,
)]
pub struct WithdrawalProof {
	/// Request commitments delivered from source to destination
	pub commitments: Vec<H256>,
	/// Request commitments on source chain
	pub source_proof: Proof,
	/// Request receipts on destination chain
	pub dest_proof: Proof,
	/// Beneficiary address and Signature from the account that delivered the message
	///  over the keccak hash of the beneficiary address
	pub beneficiary_details: Option<(Vec<u8>, Signature)>,
}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L48-92)
```rust
	pub fn accumulate(mut withdrawal_proof: WithdrawalProof) -> DispatchResult {
		// Reject duplicate commitments within the batch. The wire format is a
		// `Vec` and this extrinsic is unsigned, so this is the line of defence
		// against an attacker padding the batch with identical commitments to
		// double-claim fees.
		let mut seen = alloc::collections::BTreeSet::new();
		for key in withdrawal_proof.commitments.iter() {
			ensure!(seen.insert(key.encode()), Error::<T>::DuplicateCommitment);
		}

		// Filter out already-claimed / missing commitments
		withdrawal_proof.commitments = withdrawal_proof
			.commitments
			.into_iter()
			.filter(|req| match RequestCommitments::<T>::get(*req) {
				Some(leaf_meta) => !leaf_meta.claimed,
				// If request commitment does not exist in storage which should not be
				// possible, we skip it
				None => false,
			})
			.collect();
		ensure!(!withdrawal_proof.commitments.is_empty(), Error::<T>::MissingCommitments);
		let host = <T as Config>::IsmpHost::default();
		let source_sm = validate_state_machine(&host, withdrawal_proof.source_proof.height)
			.map_err(|_| Error::<T>::ProofValidationError)?;
		let dest_sm = validate_state_machine(&host, withdrawal_proof.dest_proof.height)
			.map_err(|_| Error::<T>::ProofValidationError)?;
		let state_machine = withdrawal_proof.source_proof.height.id.state_id;
		let source_keys = Self::source_fee_commitment_keys(
			state_machine,
			&*source_sm,
			&withdrawal_proof.commitments,
		);
		let dest_keys = dest_sm.receipts_state_trie_key(withdrawal_proof.commitments.clone());

		let source_result = Self::verify_withdrawal_proof(
			&*source_sm,
			&withdrawal_proof.source_proof,
			source_keys.clone(),
		)?;
		let dest_result = Self::verify_withdrawal_proof(
			&*dest_sm,
			&withdrawal_proof.dest_proof,
			dest_keys.clone(),
		)?;
```

**File:** modules/pallets/relayer/src/accumulate.rs (L190-211)
```rust
	fn source_fee_commitment_keys(
		state_machine: StateMachine,
		source_sm: &dyn ismp::consensus::StateMachineClient,
		commitments: &[H256],
	) -> Vec<Vec<u8>> {
		if state_machine.is_evm() {
			commitments
				.iter()
				.map(|commitment| {
					derive_unhashed_map_key_with_offset::<<T as Config>::IsmpHost>(
						commitment.0.to_vec(),
						REQUEST_COMMITMENTS_SLOT,
						0,
					)
					.0
					.to_vec()
				})
				.collect()
		} else {
			source_sm.commitment_state_trie_key(commitments.to_vec())
		}
	}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L238-302)
```rust
	pub fn validate_results(
		proof: &WithdrawalProof,
		source_keys: Vec<Vec<u8>>,
		dest_keys: Vec<Vec<u8>>,
		source_result: BTreeMap<Vec<u8>, Option<Vec<u8>>>,
		dest_result: BTreeMap<Vec<u8>, Option<Vec<u8>>>,
	) -> Result<(BTreeMap<Vec<u8>, U256>, Vec<H256>), Error<T>> {
		let mut result = BTreeMap::new();
		// Only store commitments that were claimed
		let mut commitments = Vec::new();
		for ((commitment, source_key), dest_key) in
			proof.commitments.clone().into_iter().zip(source_keys).zip(dest_keys)
		{
			let encoded_metadata =
				if let Some(encoded) = source_result.get(&source_key).cloned().flatten() {
					encoded
				} else {
					// If fee is a null value skip it, evm returns non membership proof for
					// zero values
					continue;
				};

			let fee = match proof.source_proof.height.id.state_id {
				s if crate::is_pharos(&s) =>
					if encoded_metadata.len() == 32 {
						U256::from_big_endian(&encoded_metadata)
					} else {
						return Err(Error::<T>::ProofValidationError);
					},
				s if s.is_evm() => {
					use alloy_rlp::Decodable;
					let fee = alloy_primitives::U256::decode(&mut &*encoded_metadata)
						.map_err(|_| Error::<T>::ProofValidationError)?;
					U256::from_big_endian(&fee.to_be_bytes::<32>())
				},
				s if s.is_substrate() => {
					use codec::Decode;
					let fee: u128 = pallet_ismp::dispatcher::RequestMetadata::<T>::decode(
						&mut &*encoded_metadata,
					)
					.map_err(|_| Error::<T>::ProofValidationError)?
					.fee
					.fee
					.into();
					U256::from(fee)
				},
				// unsupported
				_ => Err(Error::<T>::MismatchedStateMachine)?,
			};
			let encoded_receipt = dest_result
				.get(&dest_key)
				.cloned()
				.flatten()
				.ok_or_else(|| Error::<T>::ProofValidationError)?;
			let address = Self::decode_receipt_relayer(
				proof.dest_proof.height.id.state_id,
				&encoded_receipt,
			)?;
			let entry = result.entry(address).or_insert(U256::zero());
			*entry += fee;
			commitments.push(commitment);
		}

		Ok((result, commitments))
	}
```
