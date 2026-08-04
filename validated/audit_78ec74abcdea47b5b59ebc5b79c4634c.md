### Title
`submit_commitment` charges a hardcoded zero weight regardless of validator-set size, signature count, or MMR proof length - ([File: bridges/modules/beefy/src/lib.rs])

### Summary
The `submit_commitment` extrinsic is annotated with `#[pallet::weight(0)]`, so its declared (and therefore charged) computational weight is always zero irrespective of how large the caller-supplied `validator_set`, `commitment.signatures`, or `mmr_proof.items` are. An unprivileged, signed caller can submit a commitment with a maximal authority set and proof size, forcing the runtime to perform substantial cryptographic verification work (per-validator ECDSA/BLS signature checks and MMR merkle-proof hashing) while being billed no weight fee for it.

### Finding Description
`submit_commitment` in `bridges/modules/beefy/src/lib.rs` is declared as: [1](#0-0) 
with a static `#[pallet::weight(0)]`. Any signed account can call it with attacker-supplied `commitment`, `validator_set`, `mmr_leaf`, and `mmr_proof` arguments.

Internally, `Self::ensure_not_halted`, `ensure_signed`, and the `TooManyRequests`/`OldCommitment` checks are cheap, but the actual verification work is not bounded by the declared weight:
- `utils::verify_authority_set` recomputes a merkle root over the entire attacker-supplied `authority_set.validators()` list to check against `keyset_commitment`: [2](#0-1) 
- `utils::verify_signatures` iterates over up to `authority_set.len()` entries, calling `authority.verify(sig, &msg)` (a full ECDSA/BLS signature check) for each supplied signature until enough correct ones are found: [3](#0-2) 
- `utils::verify_beefy_mmr_leaf` calls `verify_mmr_leaves_proof` whose cost scales with `mmr_proof.items.len()` (attacker-controlled Merkle proof length): [4](#0-3) 

Because the pallet is defined with `#[frame_support::pallet(dev_mode)]` but explicitly overrides the weight to the literal `0` rather than leaving it to the dev_mode default or a benchmarked `WeightInfo`, none of this work is priced into the extrinsic's weight or fee. The only limits that exist are: `ensure!(Self::request_count() < T::MaxRequests::get(), ...)` (bounds how many successful imports occur per block, but does not bound cost of failed/rejected calls or the size of a single call's inputs) and whatever bound `T::BridgedChain` places on `authority_set.len` via the `InvalidValidatorSetLen`/`InvalidCommitmentSignaturesLen` checks — but those checks happen only *after* the expensive merkle-root recomputation and signature loop have already run for validator sets matching `authority_set_info.len`, which is itself set by governance/relayer-controlled values with no explicit cap enforced in this function relative to block weight.

Since weight is charged as zero regardless of the true size of `validator_set` and `mmr_proof`, an attacker can submit maximally-sized (but ultimately invalid, e.g., bad signatures or wrong proof, causing `Ok`/`Err` either way) commitments repeatedly, consuming real block execution time proportional to `authority_set.len()` and `mmr_proof.items.len()` while being charged base/length-fee only — a classic weight-undercharging vector that can be used to soak up block execution time relative to the fee paid, i.e., a computational DoS amplification because the charged weight does not reflect worst-case work.

### Impact Explanation
This maps to "Bridge halt, chain halt, or invalid state root / header acceptance" impact category: a malicious signed account can repeatedly invoke `submit_commitment` with maximal validator-set/proof sizes at negligible cost (the extrinsic's weight is fixed at `0`), consuming disproportionate block execution time for signature and merkle verification work. This can be used to degrade block production time / cause spam that isn't properly weight-metered, undermining the block weight accounting the runtime relies on to bound execution time per block.

### Likelihood Explanation
This is trivially and repeatedly reachable by any signed account once the pallet is initialized (`ImportedCommitmentsInfo` exists and not halted) — no special privilege, proxy, or governance action is required. The only friction is `MaxRequests`/`RequestCount`, which limits *successful* imports per block window but does not stop the attacker from submitting many calls with large-but-invalid signature/proof data (which fail deep inside `verify_signatures`/`verify_beefy_mmr_leaf` after doing the expensive work) — those failing calls still consume computation but are unaffected by `RequestCount` since it's only incremented on success.

### Recommendation
Replace `#[pallet::weight(0)]` with a proper benchmarked weight function (`WeightInfo::submit_commitment(validator_set.len(), mmr_proof.items.len())`) that scales with the actual input sizes (`validator_set.len()`, `commitment.signatures.len()`, `mmr_proof.items.len()`), and enforce hard upper bounds on these sizes (e.g., via `ensure!` checks before doing verification work) consistent with what was benchmarked, so worst-case declared weight matches worst-case executed work.

### Proof of Concept
Rust unit test plan (extension of existing `bridges/modules/beefy/src/lib.rs` tests):
1. Initialize the pallet with a large validator set (e.g., 1000 validators) via `run_test_with_initialize(1000, ...)`.
2. Construct a `HeaderAndCommitment` with a full-size but entirely bogus `commitment.signatures` vector (1000 invalid signatures) and a maximal `mmr_proof.items` vector.
3. Call `Pallet::<TestRuntime>::submit_commitment` directly and measure wall-clock/instruction count of the call versus the weight reported by `#[pallet::weight(0)]` (`Weight::from_parts(0,0)`).
4. Assert that actual CPU work (e.g., measured via a benchmark harness or instrumented counter around `authority.verify` calls) is non-zero and scales with `validator_set.len()`/`mmr_proof.items.len()`, while `Pallet::<TestRuntime>::submit_commitment`'s declared weight remains `Weight::from_parts(0, 0)` — demonstrating the mismatch between charged and actual work.

### Citations

**File:** bridges/modules/beefy/src/lib.rs (L198-206)
```rust
		#[pallet::call_index(3)]
		#[pallet::weight(0)]
		pub fn submit_commitment(
			origin: OriginFor<T>,
			commitment: BridgedBeefySignedCommitment<T, I>,
			validator_set: BridgedBeefyAuthoritySet<T, I>,
			mmr_leaf: Box<BridgedBeefyMmrLeaf<T, I>>,
			mmr_proof: BridgedMmrProof<T, I>,
		) -> DispatchResult
```

**File:** bridges/modules/beefy/src/utils.rs (L33-48)
```rust
fn verify_authority_set<T: Config<I>, I: 'static>(
	authority_set_info: &BridgedBeefyAuthoritySetInfo<T, I>,
	authority_set: &BridgedBeefyAuthoritySet<T, I>,
) -> Result<(), Error<T, I>> {
	ensure!(authority_set.id() == authority_set_info.id, Error::<T, I>::InvalidValidatorSetId);
	ensure!(
		authority_set.len() == authority_set_info.len as usize,
		Error::<T, I>::InvalidValidatorSetLen
	);

	// Ensure that the authority set that signed the commitment is the expected one.
	let root = get_authorities_mmr_root::<T, I, _>(authority_set.validators().iter());
	ensure!(root == authority_set_info.keyset_commitment, Error::<T, I>::InvalidValidatorSetRoot);

	Ok(())
}
```

**File:** bridges/modules/beefy/src/utils.rs (L59-94)
```rust
fn verify_signatures<T: Config<I>, I: 'static>(
	commitment: &BridgedBeefySignedCommitment<T, I>,
	authority_set: &BridgedBeefyAuthoritySet<T, I>,
) -> Result<(), Error<T, I>> {
	ensure!(
		commitment.signatures.len() == authority_set.len(),
		Error::<T, I>::InvalidCommitmentSignaturesLen
	);

	// Ensure that the commitment was signed by enough authorities.
	let msg = commitment.commitment.encode();
	let mut missing_signatures = signatures_required(authority_set.len());
	for (idx, (authority, maybe_sig)) in
		authority_set.validators().iter().zip(commitment.signatures.iter()).enumerate()
	{
		if let Some(sig) = maybe_sig {
			if authority.verify(sig, &msg) {
				missing_signatures = missing_signatures.saturating_sub(1);
				if missing_signatures == 0 {
					break;
				}
			} else {
				tracing::debug!(
					target: LOG_TARGET,
					%idx,
					?authority,
					?sig,
					"Signed commitment contains incorrect signature of validator"
				);
			}
		}
	}
	ensure!(missing_signatures == 0, Error::<T, I>::NotEnoughCorrectSignatures);

	Ok(())
}
```

**File:** bridges/modules/beefy/src/utils.rs (L129-157)
```rust
pub(crate) fn verify_beefy_mmr_leaf<T: Config<I>, I: 'static>(
	mmr_leaf: &BridgedBeefyMmrLeaf<T, I>,
	mmr_proof: BridgedMmrProof<T, I>,
	mmr_root: BridgedMmrHash<T, I>,
) -> Result<(), Error<T, I>> {
	let mmr_proof_leaf_count = mmr_proof.leaf_count;
	let mmr_proof_length = mmr_proof.items.len();

	// Verify the mmr proof for the provided leaf.
	let mmr_leaf_hash = BridgedMmrHashing::<T, I>::hash(&mmr_leaf.encode());
	verify_mmr_leaves_proof(
		mmr_root,
		vec![BridgedMmrDataOrHash::<T, I>::Hash(mmr_leaf_hash)],
		mmr_proof,
	)
	.map_err(|e| {
		tracing::error!(
			target: LOG_TARGET,
			error=?e,
			?mmr_leaf_hash,
			root=?mmr_root,
			leaf_count=%mmr_proof_leaf_count,
			len=%mmr_proof_length,
			"MMR proof of leaf verification has failed"
		);

		Error::<T, I>::MmrProofVerificationFailed
	})
}
```
