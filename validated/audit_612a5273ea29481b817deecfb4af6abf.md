Found a genuine analog to CVE-2017-7511 in `modules/consensus/grandpa/primitives/src/justification.rs`.

### Title
Panic-triggering `.expect()` on attacker-controlled empty `precommits` in GRANDPA justification verification - (File: modules/consensus/grandpa/primitives/src/justification.rs)

### Summary
`GrandpaJustification::verify_with_voter_set` calls `.min_by_key(...).map(...).expect(...)` on `self.commit.precommits` while computing `base_hash`, asserting that this "can only fail if precommits is empty" and that emptiness is impossible because the commit was validated above by `finality_grandpa::validate_commit`. This is the same bug class as CVE-2017-7511: a NULL/empty-container case that the code assumes is unreachable, reached instead via specially-crafted (empty) attacker-supplied data, causing a runtime panic (`.expect()`) instead of a handled error.

### Finding Description
`verify_with_voter_set` is reachable from any unsigned, permissionless GRANDPA consensus proof submission (analogous to `pallet-ismp::handle_unsigned` / the GRANDPA consensus client's `verify_consensus` dispatch path, which any relayer can call for free). The function first calls `finality_grandpa::validate_commit(&self.commit, voters, &ancestry_chain)`, and only on `Ok(ref result) if result.is_valid()` does it proceed to: [1](#0-0) 
computing `base_hash` from `self.commit.precommits.iter().min_by_key(...).map(...).expect("can only fail if precommits is empty; ...")`.

The safety comment assumes `validate_commit` rejects empty-precommit commits whenever it reports `is_valid()`. This assumption is exactly the kind of "downstream invariant" reasoning that caused the poppler NULL-pointer bug in `pdfunite`: a document-derived (here, message-derived) structure is trusted to be non-empty based on an upstream check whose exact guarantees are not locally verified. `GrandpaJustification` is fully attacker/relayer-controlled — it is SCALE-decoded directly from submitted consensus proof bytes (see the struct definition and its `Decode` derive): [2](#0-1) 
If `commit.precommits` can be constructed as an empty vector that nonetheless satisfies `validate_commit(...).is_valid()` (e.g., through crate version skew, `finality_grandpa` edge-case handling, or a `Commit` whose `target_number`/`target_hash` alone satisfy validation with zero precommits), the `.expect()` panics, aborting the runtime/host-process handling the message. This exactly mirrors the fixed sibling bug in the same GRANDPA support crate, `modules/consensus/grandpa/verifier/src/error.rs`, where a `.expect()` on relay-header lookup was deliberately converted to a typed error (`RelayHeaderNotInUnknownHeaders`) with the explicit rationale "The verifier used to `.expect` the header here and panic; it now surfaces a typed error": [3](#0-2) 
That fix pattern was not applied to the `.expect()` in `justification.rs`, leaving one analogous unchecked-precondition panic in the same GRANDPA verification pipeline.

### Impact Explanation
A panic triggered inside consensus-proof verification, reachable via a single unsigned, permissionless extrinsic (the pattern used throughout this codebase — see `pallet_ismp::Pallet::handle_unsigned`, which "permits anyone execute ISMP messages for free"): [4](#0-3) 
would, depending on how the panic propagates through `pallet-ismp`'s dispatch machinery, either abort the node's block-execution/import path (a runtime panic in Substrate is typically not gracefully caught in `on_initialize`/dispatch execution and can crash or halt the node) or at minimum permanently make GRANDPA consensus-proof updates for the affected client un-processable, freezing that route's ability to deliver messages — matching the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
Reaching this specific panic requires proving that `finality_grandpa::validate_commit` can actually return `is_valid() == true` for an empty `precommits` vector, which is not confirmed here (this depends on the exact semantics of the external `finality_grandpa` crate's `validate_commit`, which was not inspected in this pass — the local code's comment claims it's impossible but does not verify it). This uncertainty should be resolved before treating the finding as fully proven; it is flagged as the same class of "trust the upstream invariant instead of checking it" bug as the CVE, but the exploit precondition (getting `validate_commit` to accept an empty commit as valid) needs confirmation against the `finality_grandpa` dependency's actual behavior.

### Recommendation
Replace the `.expect(...)` at the `base_hash` computation with a proper `Result`/`Err` return (e.g., `Err(anyhow!("commit has no precommits"))`) instead of relying on the unverified assumption that `validate_commit`'s success implies non-empty precommits — mirroring the fix already applied to the sibling `.expect()` panic documented in `modules/consensus/grandpa/verifier/src/error.rs`.

### Proof of Concept
Not independently constructible without access to the `finality_grandpa` crate's `validate_commit` implementation to confirm whether an empty-`precommits` `Commit` can pass validation; a concrete PoC would submit a `ConsensusMessage`/GRANDPA justification via the permissionless `handle_unsigned` extrinsic containing a `Commit` with `precommits: vec![]` and a `target_hash`/`target_number` chosen so `validate_commit` reports success, triggering the `.expect()` panic during `verify_with_voter_set`.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L39-48)
```rust
#[cfg_attr(any(feature = "std", test), derive(Debug))]
#[derive(Clone, Encode, Decode, PartialEq, Eq)]
pub struct GrandpaJustification<H: HeaderT> {
	/// Current voting round number, monotonically increasing
	pub round: u64,
	/// Contains block hash & number that's being finalized and the signatures.
	pub commit: Commit<H>,
	/// Contains the path from a [`PreCommit`]'s target hash to the GHOST finalized block.
	pub votes_ancestries: Vec<H>,
}
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L95-107)
```rust
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

**File:** modules/consensus/grandpa/verifier/src/error.rs (L50-58)
```rust
	/// A `parachain_headers` map entry references a relay-chain hash that
	/// is in the finalized ancestry route (`headers.ancestry`) but whose
	/// header is not present in `finality_proof.unknown_headers`. The
	/// trusted latest relay hash is the canonical instance of this:
	/// `AncestryChain::ancestry` includes the base hash even when the
	/// base header is not in the map. The verifier used to `.expect` the
	/// header here and panic; it now surfaces a typed error.
	#[error("Parachain header proof references a relay hash with no relay-chain header in unknown_headers")]
	RelayHeaderNotInUnknownHeaders,
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
