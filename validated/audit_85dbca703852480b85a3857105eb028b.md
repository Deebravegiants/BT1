### Title
Unbounded loop / unbounded memory growth via cyclic peer-supplied GRANDPA header set causes node DoS during unsigned consensus-update dispatch - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`AncestryChain::ancestry` in `modules/consensus/grandpa/primitives/src/justification.rs` walks a peer-supplied set of headers by following `parent_hash` pointers with **no cycle detection and no depth/iteration bound**, directly mirroring the OTP TLS bug (`ssl_certificate:do_certificate_chain/7`): a cross-referencing pair of attacker-controlled records causes the walk to alternate forever while its accumulator (`route`) grows unbounded.

### Finding Description
`AncestryChain::ancestry`: [1](#0-0) 
builds a `BTreeMap<H::Hash, H>` from the attacker-supplied header list (`AncestryChain::new`, line 163-167) and then loops `while current_hash != base { current_hash = header.parent_hash(); route.push(current_hash); }`. There is no `visited` set and no maximum step count. If the submitted header set contains two headers `A` and `B` where `A.parent_hash == B.hash()` and `B.parent_hash == A.hash()` (a 2-cycle, analogous to the cross-signed cert pair in the TLS CVE), and neither equals `base`, the lookup in the `BTreeMap` will always succeed for both hashes, so `current_hash` will never equal `base`; the loop runs forever, and `route` grows without bound (unbounded `Vec` allocation), exactly like the CVE's unbounded chain accumulator.

This function is reachable from fully untrusted, unauthenticated input:
- `pallet_ismp::Pallet::handle_unsigned` is declared `ensure_none(origin)` — an **unsigned extrinsic that anyone can submit for free**: [2](#0-1) 
- It calls `Self::execute(messages)` → ISMP's `handlers::consensus::update_client`, which calls `consensus_client.verify_consensus(...)` with the attacker-supplied `msg.consensus_proof`: [3](#0-2) 
- `GrandpaConsensusClient::verify_consensus` decodes the attacker-controlled `ConsensusMessage` and, for the `StandaloneChain` variant, calls `verify_grandpa_finality_proof(consensus_state, standalone_chain_message.finality_proof)`, entirely from attacker bytes: [4](#0-3) 
- `verify_grandpa_finality_proof` builds `AncestryChain` directly from `finality_proof.unknown_headers` (attacker-supplied) and calls `.ancestry(...)` twice on it: [5](#0-4) 
- It also calls `justification.verify(...)`, which further calls `verify_with_voter_set`, constructing a second `AncestryChain` from `self.votes_ancestries` (also attacker-supplied) and invoking `.ancestry(...)` once per precommit: [6](#0-5) 

Both `unknown_headers` and `votes_ancestries` are raw, SCALE-decoded, attacker-controlled `Vec<H>` with no validation that the parent-hash graph is acyclic before the walk executes.

### Impact Explanation
Because `handle_unsigned` is dispatchable by any unauthenticated relayer for free and its declared weight does not scale with the pathological cost of a cyclic header graph, a single crafted extrinsic can drive the executing node's runtime into an effectively infinite loop with unbounded `Vec` growth. This can hang or OOM-crash the node evaluating the block (validator/collator) or, at minimum, consume unbounded resources disproportionate to the paid weight, denying consensus-client updates and therefore blocking all downstream message delivery through that consensus client — a "route unable to deliver messages" condition, consistent with the scope's accepted impact categories.

### Likelihood Explanation
Likelihood is high for an attacker able to submit unsigned extrinsics (any relayer/message dispatcher): constructing two headers whose `parent_hash` fields point at each other (with arbitrary content otherwise, since the loop runs before/independent of justification signature verification for the `unknown_headers` ancestry calls in `verify_grandpa_finality_proof`) is straightforward and requires no privileged access, no valid signatures for the ancestry walk itself, and no completed prior state.

### Recommendation
In `AncestryChain::ancestry`, track visited hashes (e.g., a `BTreeSet`) and reject/return an error if a hash is revisited before reaching `base`, and/or bound the maximum number of iterations to the number of headers supplied (`self.ancestry.len()`), mirroring the bound already applied in `modules/consensus/pharos/primitives/src/spv.rs` (`MAX_PROOF_DEPTH` checks). Apply this fix before the ancestry walk is invoked from `verify_grandpa_finality_proof` and `GrandpaJustification::verify_with_voter_set`.

### Proof of Concept
1. Craft two headers `A`, `B` such that `A.parent_hash() == B.hash()` and `B.parent_hash() == A.hash()`.
2. Include them in `finality_proof.unknown_headers` (or `votes_ancestries`) of a `ConsensusMessage::StandaloneChain` proof, choosing `base`/`target` such that the walk starting at `A` or `B` never reaches `base` (e.g., set `base` to a hash not present in the header set).
3. Submit via `pallet_ismp::Pallet::handle_unsigned` as an unsigned extrinsic.
4. `verify_grandpa_finality_proof` → `AncestryChain::ancestry(base, target.hash())` (or the ancestry call in `verify_with_voter_set`) enters the alternating `A ⇄ B` loop, growing `route` without bound and never terminating, hanging/crashing the executing node.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L73-127)
```rust
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

		let mut visited_hashes = BTreeSet::new();
		for signed in self.commit.precommits.iter() {
			let message = finality_grandpa::Message::Precommit(signed.precommit.clone());

			check_message_signature::<_, _>(
				&message,
				&signed.id,
				&signed.signature,
				self.round,
				set_id,
			)?;

			if base_hash == signed.precommit.target_hash {
				continue;
			}

			let route = ancestry_chain
				.ancestry(base_hash, signed.precommit.target_hash)
				.map_err(|_| anyhow!("[verify_with_voter_set] Invalid ancestry!"))?;
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L180-197)
```rust
	fn ancestry(
		&self,
		base: H::Hash,
		block: H::Hash,
	) -> Result<Vec<H::Hash>, finality_grandpa::Error> {
		let mut route = vec![block];
		let mut current_hash = block;
		while current_hash != base {
			match self.ancestry.get(&current_hash) {
				Some(current_header) => {
					current_hash = *current_header.parent_hash();
					route.push(current_hash);
				},
				_ => return Err(finality_grandpa::Error::NotDescendent),
			};
		}
		Ok(route)
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

**File:** modules/ismp/core/src/handlers/consensus.rs (L29-46)
```rust
pub fn update_client<H>(host: &H, msg: ConsensusMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	let consensus_client_id = host.consensus_client_id(msg.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized { consensus_state_id: msg.consensus_state_id },
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	let trusted_state = host.consensus_state(msg.consensus_state_id)?;
	host.is_consensus_client_frozen(msg.consensus_state_id)?;
	host.is_expired(msg.consensus_state_id)?;

	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L169-174)
```rust
			ConsensusMessage::StandaloneChain(standalone_chain_message) => {
				let (consensus_state, header, _, _) = verify_grandpa_finality_proof(
					consensus_state,
					standalone_chain_message.finality_proof,
				)?;

```

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L52-88)
```rust
	// First validate unknown headers.
	let headers = AncestryChain::<H>::new(&finality_proof.unknown_headers);

	let target = finality_proof
		.unknown_headers
		.iter()
		.max_by_key(|h| *h.number())
		.ok_or(Error::UnknownHeadersEmpty)?;

	// this is illegal
	if target.hash() != finality_proof.block {
		Err(Error::LatestBlockMismatch)?;
	}

	let justification =
		GrandpaJustification::<H>::decode_all(&mut &finality_proof.justification[..])
			.map_err(|e| Error::DecodeJustification(alloc::format!("{e:?}")))?;

	if justification.commit.target_hash != finality_proof.block {
		Err(Error::JustificationTargetMismatch)?;
	}

	let from = consensus_state.latest_hash;

	let base = finality_proof
		.unknown_headers
		.iter()
		.min_by_key(|h| *h.number())
		.ok_or(Error::UnknownHeadersEmpty)?;

	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
```
