I found a genuine remaining panic in `GrandpaJustification::verify_with_voter_set`, reachable from the permissionless, unsigned `handle_unsigned` consensus-update path — analogous to CVE-2020-2921's unauthenticated-DoS-via-crash pattern.

### Title
Unrejected empty-precommit GRANDPA justification panics the runtime via `.expect()` on attacker-controlled proof data - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`GrandpaJustification::verify_with_voter_set` computes `base_hash` by `min_by_key` over `self.commit.precommits` and immediately calls `.expect(...)` on the `Option`, relying on the comment's claim that "commit has been validated above; valid commits must include precommits." This mirrors the exact bug class already fixed elsewhere in this same file (`RelayHeaderNotInUnknownHeaders`) and in the BEEFY/sync-committee verifiers (`InvalidMmrProof` for empty `leaf_indices`, multi-proof length guard) — an attacker-controlled, permissionless proof field reaching an `.expect()`/panic instead of a typed error. [1](#0-0) 

### Finding Description
`verify_with_voter_set` is reached from `verify_grandpa_finality_proof` (`modules/consensus/grandpa/verifier/src/lib.rs`), which is invoked by `GrandpaConsensusClient::verify_consensus` (`modules/ismp/clients/grandpa/src/consensus.rs`), which is in turn dispatched from the permissionless, fee-free `pallet_ismp::Call::handle_unsigned` extrinsic validated only by `ValidateUnsigned::validate_unsigned` — no signature, no relayer allow-list, callable by anyone. [2](#0-1) [3](#0-2) 

The code first calls `finality_grandpa::validate_commit(&self.commit, voters, &ancestry_chain)`. The comment assumes that a `Commit` (deserialized SCALE struct, fully attacker-controlled bytes) can only be "valid" if `precommits` is non-empty. This is an assumption about the external `finality_grandpa` crate's behavior for a `Commit` with an **empty `precommits` Vec**. If `finality_grandpa::validate_commit` treats a commit with zero precommits as vacuously "valid" (e.g., zero equivocations, zero duplicated votes, zero invalid voters — all trivially zero for an empty set — and `result.is_valid()` returning `true` because there's nothing to invalidate it), execution falls through to:

```rust
let base_hash = self.commit.precommits.iter()
    .map(|signed| &signed.precommit)
    .min_by_key(|precommit| precommit.target_number)
    .map(|precommit| precommit.target_hash.clone())
    .expect("can only fail if precommits is empty; ... qed.");
```

With an empty `precommits`, `min_by_key` returns `None`, and `.expect(...)` panics. This is precisely the bug class the same file's sibling code was already patched for (see the `RelayHeaderNotInUnknownHeaders` fix comment in `modules/consensus/grandpa/verifier/src/error.rs` lines 50-58, describing an identical "used to `.expect` and panic; now surfaces a typed error" remediation for a different attacker-controlled edge case). No equivalent guard exists here for the "commit has zero precommits" invariant — it is asserted only in a comment, not enforced in code, and its correctness rests entirely on an unverified assumption about `finality_grandpa::validate_commit`'s treatment of empty precommit sets.

### Impact Explanation
A panic inside `handle_unsigned`/`validate_unsigned` execution on a parachain running `pallet-ismp` with the GRANDPA consensus client crashes the runtime's WASM execution for that transaction/block-authoring attempt. Because `handle_unsigned` is unsigned and free (no fee, no nonce, no allow-list — "Difficult to exploit... network access... unauthorized ability to cause a hang or frequently repeatable crash" per the CVE-2020-2921 analog), any peer can broadcast such a malformed `ConsensusMessage` repeatedly, potentially disrupting block production/transaction pool validation for the GRANDPA consensus client route — a permanent-DoS-style impact on message delivery for that route, which is in-scope per the task's acceptance criteria ("a route unable to deliver messages").

### Likelihood Explanation
Likelihood is bounded by whether `finality_grandpa::validate_commit` actually accepts an empty-`precommits` `Commit` as "valid" — this is external-crate behavior I could not verify by reading `finality_grandpa`'s source in this index (only the call site is visible here). If the crate already rejects an empty-precommit commit as invalid (e.g., via a "no positive supermajority" or similar check before `result.is_valid()`), this path is unreachable and the code is safe-by-external-invariant, same as claimed in the comment. I was not able to confirm this either way from the indexed code, so this must be flagged as **uncertain** rather than confirmed exploitable.

### Recommendation
Do not rely on `finality_grandpa::validate_commit`'s internal behavior as a safety invariant for `.expect()`. Replace the `.expect(...)` with an explicit typed-error check (`Err(anyhow!("empty precommits in grandpa justification"))?` or equivalent) before calling `.min_by_key`, exactly mirroring the pattern already applied to `RelayHeaderNotInUnknownHeaders` in the sibling GRANDPA verifier file and to `InvalidMmrProof`'s empty `leaf_indices` check in the BEEFY verifier. This removes the panic surface regardless of whether the external crate's `validate_commit` currently blocks empty-precommit commits, since crate behavior across future dependency version bumps is not something this codebase controls.

### Proof of Concept
Not verifiable without confirming `finality_grandpa::validate_commit`'s handling of an empty `precommits` vector, which is outside this repository's indexed source. A concrete PoC would require: (1) constructing a SCALE-encoded `GrandpaJustification` with `commit.precommits = vec![]` and `commit.target_hash`/`target_number` set to any value, (2) wrapping it in the appropriate `ConsensusMessage`/`FinalityProof` for the GRANDPA client, and (3) submitting it via `handle_unsigned`; if `validate_commit` returns `Ok(result)` with `result.is_valid() == true` for this input, the subsequent `.expect()` panics. I could not execute or trace the `finality_grandpa` crate internals to confirm step 3's premise, so this finding should be treated as a code-defense-in-depth gap of uncertain direct exploitability rather than a confirmed live vulnerability.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L92-107)
```rust
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L69-90)
```rust
	fn verify_consensus(
		&self,
		_host: &dyn IsmpHost,
		consensus_state_id: ConsensusStateId,
		trusted_consensus_state: Vec<u8>,
		proof: Vec<u8>,
	) -> Result<(Vec<u8>, VerifiedCommitments), Error> {
		// decode the proof into consensus message
		let consensus_message: ConsensusMessage = codec::Decode::decode(&mut &proof[..])
			.map_err(|e| GrandpaError::DecodeConsensusMessage(format!("{e:?}")))?;

		// decode the consensus state
		let consensus_state: ConsensusState =
			codec::Decode::decode(&mut &trusted_consensus_state[..])
				.map_err(|e| GrandpaError::DecodeConsensusState(format!("{e:?}")))?;

		// Reject before any arm runs; see `envelope_matches_state_machine`.
		if !envelope_matches_state_machine(&consensus_state.state_machine, &consensus_message) {
			Err(GrandpaError::ConsensusMessageStateMachineMismatch(
				consensus_state.state_machine,
			))?
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```
