### Title
Unchecked Empty-Precommits Invariant Leads to Panic in GRANDPA Justification Verification - (`modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`GrandpaJustification::verify_with_voter_set` derives `base_hash` from `self.commit.precommits` using `.min_by_key(...).map(...).expect(...)`, where the `.expect()` message asserts "can only fail if precommits is empty; commit has been validated above; valid commits must include precommits; qed." This assumption is never independently checked in this codebase — it relies entirely on an external crate (`finality_grandpa::validate_commit`) always rejecting an empty `precommits` vector. `commit.precommits` is SCALE-decoded straight from an attacker-supplied consensus proof with no length floor, so if any code path allows `validate_commit` to return a "valid" (`is_valid() == true`) result for an empty precommit set, execution falls through the guarding `match` and the `.expect()` panics. This mirrors the CVE-2022-0907 bug class: a caller trusts an unverified validation return signal instead of directly checking the invariant it needs (non-empty precommits) before dereferencing/using the data.

### Finding Description [1](#0-0) 

`verify_with_voter_set` is the core cryptographic check for GRANDPA finality proofs: it validates the commit via `finality_grandpa::validate_commit`, and only after that branch succeeds does it compute `base_hash` from the lowest-target precommit — using `.expect()` rather than an explicit `Err` return, on the stated belief that a "valid" commit result guarantees `precommits` is non-empty: [2](#0-1) 

Unlike the sibling fixes already present elsewhere in this codebase for the exact same bug class — e.g. the BEEFY MMR `leaf_indices` empty-vector guard, the Pharos SPV `nibble_at_depth`/`MAX_PROOF_DEPTH` guards, and the Ethereum trie `node_codec` empty-HP-prefix guard, all of which replaced a panic with a typed `Err` after finding that "validated" input could still be adversarially empty — the GRANDPA path here still relies on an implicit invariant enforced by an external, unaudited-in-repo crate rather than an explicit check in `hyperbridge`'s own code: [3](#0-2) [4](#0-3) [5](#0-4) 

This GRANDPA verification path is reachable from `pallet-ismp`'s permissionless unsigned extrinsic: [6](#0-5) [7](#0-6) 

which is exactly the class of surface named in scope ("consensus verification ... GRANDPA ... pallet-ismp handle_unsigned").

### Impact Explanation
If `finality_grandpa::validate_commit` can return an `Ok` result whose `.is_valid()` is `true` for a `Commit` with zero precommits (a possibility this repository does not itself defend against, since `commit.precommits` is just a `Vec` from SCALE decoding with no length floor and the guarding branch only inspects `duplicated_precommits`/`invalid_voters`/`equivocations` counts, not emptiness), then `.expect()` on the `None` returned by `.min_by_key().map()` over an empty iterator panics. A panic while validating an unsigned extrinsic in `validate_unsigned`/`handle_unsigned` is executed inside the runtime and would trap block execution or transaction-pool validation for every collator processing that proof — a denial-of-service against the whole parachain's ability to process ISMP consensus updates and, transitively, every relayed request/response routed through GRANDPA-secured (Kusama/Polkadot relay-anchored) state machines, matching the "route unable to deliver messages" impact bar.

### Likelihood Explanation
The attack requires only submitting a `ConsensusMessage` carrying a `GrandpaJustification` whose `commit.precommits` is empty — a single unsigned, permissionless transaction from any external account, no privileged role needed. The remaining uncertainty is whether the vendored `finality_grandpa` crate's `validate_commit` can be coaxed (e.g. via a maliciously constructed `VoterSet`/threshold edge case, or a future crate version change) into reporting success for zero precommits; this repository's own defense-in-depth pattern elsewhere (explicitly re-checking invariants that upstream/library code is "supposed" to guarantee) suggests the team does not trust such implicit guarantees at trust boundaries, and this file is the one remaining place following the old pattern rather than the now-standard "verify, don't assume" pattern used in the BEEFY, Pharos and Ethereum-trie fixes.

### Recommendation
Replace the `.expect(...)` in `verify_with_voter_set` with an explicit, defensive check: reject the justification with a typed error (e.g. `Err(anyhow!("empty precommits in grandpa justification"))`) if `self.commit.precommits.is_empty()`, evaluated independently of `finality_grandpa::validate_commit`'s result, mirroring the guard patterns already added for BEEFY's `leaf_indices`, the Pharos SPV depth/nibble checks, and the Ethereum trie HP-prefix decode.

### Proof of Concept
Root cause is confirmed in-repo; full exploitability depends on the external `finality_grandpa` crate's `validate_commit` behavior for zero-length precommits, which is outside this repository and not independently re-verified here — this could not be fully confirmed with the tools available. Conceptually:
1. Craft a `ConsensusMessage` whose decoded proof contains a `GrandpaJustification` with `commit.precommits = vec![]` and `votes_ancestries = vec![]`.
2. Submit it via `pallet_ismp::Call::handle_unsigned` (`modules/pallets/ismp/src/lib.rs:373`) as an unsigned extrinsic.
3. If `finality_grandpa::validate_commit` reports `is_valid() == true` for this input (unverified against the vendored crate version), execution reaches `.expect()` in `justification.rs:102`, panicking during unsigned-extrinsic validation/execution.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L65-107)
```rust
	/// Validate the commit and the votes' ancestry proofs.
	pub fn verify_with_voter_set(
		&self,
		set_id: u64,
		voters: &VoterSet<AuthorityId>,
	) -> Result<(), anyhow::Error> {
		use finality_grandpa::Chain;

		let ancestry_chain = AncestryChain::<H>::new(&self.votes_ancestries);

		match finality_grandpa::validate_commit(&self.commit, voters, &ancestry_chain) {
			Ok(ref result) if result.is_valid() => {
				if result.num_duplicated_precommits() > 0 ||
					result.num_invalid_voters() > 0 ||
					result.num_equivocations() > 0
				{
					Err(anyhow!("Invalid commit, found one of `duplicate precommits`, `invalid voters`, or `equivocations` {result:?}"))?
				}
			},
			err => {
				let result = err.map_err(|_| {
					anyhow!("[verify_with_voter_set] Invalid ancestry while validating commit!")
				})?;
				Err(anyhow!("invalid commit in grandpa justification: {result:?}"))?
			},
		}

		// we pick the precommit for the lowest block as the base that
		// should serve as the root block for populating ancestry (i.e.
		// collect all headers from all precommit blocks to the base)
		let base_hash = self
			.commit
			.precommits
			.iter()
			.map(|signed| &signed.precommit)
			.min_by_key(|precommit| precommit.target_number)
			.map(|precommit| precommit.target_hash.clone())
			.expect(
				"can only fail if precommits is empty; \
				 commit has been validated above; \
				 valid commits must include precommits; \
				 qed.",
			);
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L225-237)
```rust
fn verify_mmr_leaf<H: Keccak256 + Send + Sync>(
	mmr: &MmrProof,
	mmr_root: H256,
) -> Result<(), Error> {
	// `leaf_indices` is supplied by the relayer in the unsigned consensus message;
	// an empty vector previously panicked the runtime via the unchecked `[0]` index
	// after the BEEFY signature and authority membership checks had already succeeded.
	// This verifier checks a single MMR leaf, so reject any proof that does not carry
	// exactly one leaf index.
	if mmr.mmr_proof.leaf_indices.len() != 1 {
		Err(Error::InvalidMmrProof)?
	}
	let leaf_index = mmr.mmr_proof.leaf_indices[0];
```

**File:** modules/trees/ethereum/src/tests.rs (L73-85)
```rust
#[test]
fn empty_hp_prefix_returns_error_not_panic() {
	// Regression: a leaf/extension node is RLP-encoded as a 2-item list whose
	// first item is the hex-prefix-encoded partial key. Before the fix at
	// `node_codec.rs` the decoder indexed `data[0]` without checking that the
	// HP payload was non-empty, so an adversarial proof node of the form
	// `rlp([b"", b""])` panicked with index-out-of-bounds inside on-chain
	// execution (e.g. parachain block verification). It must now return an
	// `Err` cleanly.
	let adversarial_node: [u8; 3] = [0xc2, 0x80, 0x80];
	let result = <RlpNodeCodec<KeccakHasher> as NodeCodec>::decode_plan(&adversarial_node);
	assert!(result.is_err(), "decoder must reject empty HP prefix, got {:?}", result);
}
```

**File:** modules/consensus/sync-committee/verifier/src/lib.rs (L184-192)
```rust
	// `calculate_multi_merkle_root` panics on a short `multi_proof` because its final
	// `objects.get(&GeneralizedIndex(1)).unwrap()` cannot reconstruct the root. Reject
	// proofs whose helper-node count does not match what the algorithm requires so an
	// attacker-controlled `multi_proof` cannot panic the runtime via the public unsigned
	// consensus update path.
	if execution_payload.multi_proof.len() != get_helper_indices(&execution_payload_indices).len()
	{
		Err(Error::InvalidMerkleBranch("Execution payload multiproof length".into()))?;
	}
```

**File:** modules/pallets/ismp/src/lib.rs (L358-382)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
		///
		/// Emits different message events based on the Message received if successful.
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L604-626)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T> {
		type Call = Call<T>;

		// empty pre-dispatch do we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;

```
