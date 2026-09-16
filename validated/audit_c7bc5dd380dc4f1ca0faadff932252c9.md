## Analysis

The reported bug class — a challenge-protocol state check that can never resolve because it only looks for "does a rival exist" rather than "has this assertion actually been confirmed" — maps directly onto Hyperbridge's Arbitrum BoLD consensus verifier.

### Title
Arbitrum BoLD consensus client permanently rejects a confirmed assertion branch once a rival was ever created for its parent - (File: `modules/ismp/clients/arbitrum/src/lib.rs`)

### Summary
`verify_arbitrum_bold` gates acceptance of a new Arbitrum state commitment on the parent assertion's `secondChildBlock` field being zero, treating any non-zero value as "this branch is being challenged" and permanently rejecting the proof. Because `secondChildBlock` is a write-once field on Arbitrum's `RollupCore` that never resets after a rival child is created — even once BoLD's own dispute-resolution machinery (edge trackers / `confirmByTime`) confirms one of the two children as canonical — this check remains permanently true, so Hyperbridge can never again accept a state commitment descending from that parent, regardless of the eventual, correct on-chain outcome.

### Finding Description
`verify_arbitrum_bold` reads the parent assertion's first storage word and rejects the proof with `Error::AssertionChallenged` whenever `secondChildBlock != 0`: [1](#0-0) 

The code comment itself documents the semantics being tested: *"a parent with two children is being contested"* — i.e. the check is meant to reject only assertions that are *currently* in dispute. But Arbitrum's `AssertionNode.secondChildBlock` is set exactly once, at the moment the second (rival) child is created, and is never cleared or updated once the dispute is later resolved (via `confirmAssertion`/`confirmByTime` on the honest branch). This mirrors precisely the external report's root cause: a check keyed off "has a rival ever appeared" rather than "is this assertion confirmed" can never un-trip once tripped, because there is no code path that re-evaluates the state once the underlying dispute reaches its terminal, honest outcome.

The client-side wiring confirms this check is unconditional and mandatory on every BoLD proof: [2](#0-1) 

and the off-chain relayer (`arb-host`) fetches exactly this parent storage slot for every new assertion it relays: [3](#0-2) 

There is no alternate path in this module that checks whether the specific assertion being proven was the one ultimately confirmed by the real rollup (e.g. checking the assertion's own confirmed/created status, or that it is on the currently-canonical chain via `latestConfirmed`), only the boolean "did this parent ever spawn two children." Consequently, the very first legitimate challenge on Arbitrum for a given branch — honest or not — permanently blocks Hyperbridge's Arbitrum consensus client from ever ingesting any further state for that lineage, since the parent's `secondChildBlock` byte pattern can never revert to zero.

### Impact Explanation
This causes a permanent denial of the ISMP route for the affected Arbitrum-family state machine: once any assertion under a given parent is challenged, no subsequent state commitment (even the one Arbitrum itself confirms as canonical) can ever be verified again through `verify_arbitrum_bold`. That freezes all cross-chain message delivery (dispatch of POST/GET requests and responses, and any HyperFungibleToken / intents flows) that depend on state proofs against this Arbitrum state machine, matching the "route unable to deliver messages" acceptance criterion. Nothing in the module offers recovery other than reconfiguring or upgrading the consensus client, since fisherman blacklisting only removes fraudulent claims — it does not restore this permanently-tripped legitimate check.

### Likelihood Explanation
Likelihood is Medium: this triggers on ordinary, permissionless BoLD activity — any party can create a rival assertion against a pending node (this is a designed, expected part of Arbitrum's optimistic challenge protocol, not an attack), and once that happens the freeze is unconditional and irreversible for that lineage, with no special privileges required to trigger it.

### Recommendation
- Short term: instead of (or in addition to) checking the parent's `secondChildBlock`, check the confirmation status specific to the assertion actually being proven (e.g., verify against the rollup's `latestConfirmed`/assertion status, or that the assertion node itself is marked confirmed), so a resolved dispute no longer blocks proofs of the confirmed branch.
- Long term: document the full BoLD assertion lifecycle (pending → challenged → confirmed) that this verifier is meant to track, and add regression tests covering the "challenged-then-confirmed" case, not just the "never challenged" and "currently challenged" cases.

### Proof of Concept
1. On Arbitrum, an assertion `A` is created; a rival assertion `A'` is submitted against the same parent `P`, setting `P.secondChildBlock != 0`.
2. Arbitrum's own dispute resolution eventually confirms `A` (or `A'`) as canonical via `confirmAssertion`/timeout logic — the rollup itself now accepts this branch.
3. A relayer submits an `ArbitrumBoldProof` for a child of the confirmed assertion to Hyperbridge via `verify_arbitrum_bold`.
4. The verifier reads `P`'s first storage word and finds `secondChildBlock != 0` (unchanged since step 1), returning `Error::AssertionChallenged` regardless of the now-resolved, confirmed state — see the check at [4](#0-3) . No proof for this lineage will ever be accepted again.

### Citations

**File:** modules/ismp/clients/arbitrum/src/lib.rs (L342-365)
```rust
	// BoLD encodes challenges implicitly: a parent with two children is being contested. The
	// parent's `AssertionNode.secondChildBlock` (uint64 at struct offset 8) is non-zero iff a
	// rival sibling exists. Read the parent's first storage word from the proof and check the
	// secondChildBlock bytes.
	let parent_key =
		derive_map_key::<H>(payload.previous_assertion_hash.0.to_vec(), ASSERTIONS_SLOT);
	let parent_word_raw =
		get_value_from_proof::<H>(parent_key.0.to_vec(), storage_root, payload.challenge_proof)?
			.ok_or(Error::ParentAssertionNotFound)?;
	let parent_word_bytes = <alloy_primitives::Bytes as Decodable>::decode(&mut &*parent_word_raw)
		.map_err(|_| Error::DecodeParentAssertionWord(format!("{:?}", parent_word_raw)))?
		.0
		.to_vec();
	if parent_word_bytes.len() > 32 {
		Err(Error::ParentAssertionTooLong)?
	}
	let mut word = vec![0u8; 32 - parent_word_bytes.len()];
	word.extend_from_slice(&parent_word_bytes);
	// Layout: [padding(16) || secondChildBlock(8) || firstChildBlock(8)] in big-endian. So
	// secondChildBlock occupies bytes word[16..24].
	const ZERO_U64: [u8; 8] = [0u8; 8];
	if &word[16..24] != ZERO_U64.as_slice() {
		Err(Error::AssertionChallenged)?
	}
```

**File:** modules/ismp/clients/ismp-arbitrum/src/lib.rs (L176-196)
```rust
				ArbitrumConsensusProof::ArbitrumBold(proof) => {
					// BoLD assertions use the on-chain `assertionHash` directly as the claim key.
					let assertion_hash = compute_assertion_hash(
						proof.previous_assertion_hash,
						proof.after_state.hash(),
						proof.sequencer_batch_acc,
					);
					if <T as pallet::Config>::FishermanBlacklist::is_arbitrum_claim_blacklisted(
						state_machine_id,
						assertion_hash,
					) {
						return Err(ArbitrumError::ClaimBlacklisted(assertion_hash).into());
					}

					let state = verify_arbitrum_bold::<H>(
						proof,
						state_root,
						rollup_core_address,
						consensus_state_id.clone(),
					)?;

```

**File:** tesseract/consensus/arb-host/src/lib.rs (L259-324)
```rust
	pub async fn fetch_arbitrum_bold_payload(
		&self,
		at: u64,
		event: IRollupBold::AssertionCreated,
	) -> Result<ArbitrumBoldProof, anyhow::Error> {
		let assertion_hash_key =
			derive_map_key(event.assertionHash.0.to_vec(), ASSERTIONS_SLOT as u64);
		// `_assertions[parent]` storage key — first struct slot holds `firstChildBlock` and
		// `secondChildBlock` and is what the verifier inspects to prove "not challenged".
		let parent_assertion_key =
			derive_map_key(event.parentAssertionHash.0.to_vec(), ASSERTIONS_SLOT as u64);
		let rollup_addr = Address::from_slice(&self.rollup_core.0);
		let proof = self
			.beacon_execution_client
			.get_proof(
				rollup_addr,
				vec![
					B256::from_slice(&assertion_hash_key.0),
					B256::from_slice(&parent_assertion_key.0),
				],
			)
			.block_id(at.into())
			.await?;
		let arb_block_hash: H256 = event.assertion.afterState.globalState.bytes32Vals[0].0.into();
		let arbitrum_header = self.fetch_header(arb_block_hash).await?;
		let global_state = RustGlobalState {
			block_hash: arb_block_hash.0.into(),
			send_root: event.assertion.afterState.globalState.bytes32Vals[1].0.into(),
			inbox_position: event.assertion.afterState.globalState.u64Vals[0],
			position_in_message: event.assertion.afterState.globalState.u64Vals[1],
		};

		let machine_status = event
			.assertion
			.afterState
			.machineStatus
			.try_into()
			.map_err(|_| anyhow!("Failed conversion"))?;

		let after_state = AssertionState {
			global_state,
			machine_status,
			end_history_root: event.assertion.afterState.endHistoryRoot.0.into(),
		};

		let storage_proof_entry = |idx: usize, what: &str| -> Result<Vec<Vec<u8>>, anyhow::Error> {
			Ok(proof
				.storage_proof
				.get(idx)
				.cloned()
				.ok_or_else(|| anyhow!("Storage proof not found for arbitrum {what}"))?
				.proof
				.into_iter()
				.map(|node| node.to_vec())
				.collect())
		};

		let payload = ArbitrumBoldProof {
			arbitrum_header,
			after_state,
			previous_assertion_hash: event.parentAssertionHash.0.into(),
			sequencer_batch_acc: event.afterInboxBatchAcc.0.into(),
			storage_proof: storage_proof_entry(0, "assertion hash")?,
			contract_proof: proof.account_proof.iter().cloned().map(|node| node.to_vec()).collect(),
			challenge_proof: storage_proof_entry(1, "parent assertion")?,
		};
```
