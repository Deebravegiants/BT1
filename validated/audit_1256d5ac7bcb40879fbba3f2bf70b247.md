## Title
Unbounded/cyclic ancestry walk in GRANDPA justification verification causes permanent node hang (DoS) - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
The GRANDPA consensus client's ancestry-resolution routine walks a parent-hash chain built entirely from attacker-supplied header data, with no cycle detection and no depth bound. A relayer can submit a `handle_unsigned` extrinsic containing a GRANDPA consensus message whose justification includes a `votes_ancestries` (or `unknown_headers`) set forming a hash cycle that never reaches the expected base hash. The verifier's `ancestry()` walk then loops forever (and grows an unbounded `Vec` every iteration), hanging block execution — the same "attacker-controlled input drives the query engine into a non-terminating/resource-exhausting loop" bug class as CVE-2018-3203.

### Finding Description
`AncestryChain::ancestry` walks parent hashes from `block` back to `base` using a `BTreeMap` built from the untrusted header list: [1](#0-0) 

There is no loop bound, no maximum-depth guard, and no protection against a cycle among the supplied headers. Because `H::hash()` is computed purely from the header's own fields (including its `parent_hash` field, which is attacker-set data, not a value that must chain to any real block), an attacker can construct two (or more) synthetic headers `A` and `B` where `A.parent_hash == B.hash()` and `B.parent_hash == A.hash()`. As long as this cycle does not include the trusted `base`/`from` hash, `while current_hash != base { ... }` never terminates: `current_hash` alternates between `A` and `B` forever, and `route.push(current_hash)` grows unboundedly, causing an out-of-memory crash if the CPU-bound infinite loop doesn't hang the executor first.

This function is reached from two attacker-controlled entry points:
1. `GrandpaJustification::verify_with_voter_set`, which builds `AncestryChain::<H>::new(&self.votes_ancestries)` and calls `finality_grandpa::validate_commit(...)` (which internally queries `Chain::ancestry`) **before** `check_message_signature` is invoked in the precommit loop, and again directly via `ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)`: [2](#0-1) [3](#0-2) 

2. `verify_grandpa_finality_proof`, which builds `AncestryChain::<H>::new(&finality_proof.unknown_headers)` from the relayed `FinalityProof` and calls `headers.ancestry(from, target.hash())` directly: [4](#0-3) 

Both are ultimately reachable from the unsigned, permissionless `handle_unsigned` extrinsic in `pallet-ismp`, which executes any submitted `Message` — including `ConsensusMessage`s that route into `GrandpaConsensusClient::verify_consensus`: [5](#0-4) [6](#0-5) 

Notably, other consensus/proof-verification code paths in this same codebase (e.g., the Pharos SPV verifier and GRANDPA fraud-proof paths) explicitly document and enforce bounded proof depth to prevent exactly this class of bug (`MAX_PROOF_DEPTH`, `ProofTooDeep`), showing the project is aware of the risk elsewhere but the core `AncestryChain::ancestry` walk lacks the same protection: [7](#0-6) 

### Impact Explanation
This is a permissionless, unauthenticated denial-of-service: no valid GRANDPA signatures, no valid authority set membership, and no state proof are required to trigger the infinite loop in `validate_commit`'s Chain trait usage — only a structurally consistent set of "unknown headers"/`votes_ancestries` forming a cycle not containing the trusted base hash. A single crafted `handle_unsigned` extrinsic can hang the collator/validator executing the block, halting message delivery for the entire chain (route unable to deliver messages) and threatening liveness of all cross-chain flows relying on the GRANDPA client.

### Likelihood Explanation
High. `handle_unsigned` is explicitly designed to let anyone submit ISMP messages "for free" as long as they decode; no signature or fee is required. Constructing two Substrate-header structs whose `parent_hash` fields point at each other's `hash()` is straightforward (no cryptographic obstacle — the header hash function does not enforce any chain-of-custody beyond hashing the header's own byte fields), and no size limit exists to reject the resulting `votes_ancestries`/`unknown_headers` array before the ancestry walk runs.

### Recommendation
Harden `AncestryChain::ancestry` (and any related header-map ancestry walker) to:
- Bound the number of loop iterations to at most the number of unique supplied headers (`self.ancestry.len() + 1`), returning `Error::NotDescendent` (or an equivalent typed error) once that bound is exceeded.
- Alternatively, track `visited` hashes in a `BTreeSet` during the walk and abort with an error the moment a hash repeats, explicitly rejecting cyclic ancestry data.
- Apply this fix uniformly everywhere `AncestryChain::ancestry` is called (`justification.rs::verify_with_voter_set`, `verifier/lib.rs::verify_grandpa_finality_proof`, and the fraud-proof path in `modules/ismp/clients/grandpa/src/consensus.rs`).

### Proof of Concept
1. Construct header `B` with arbitrary `number`/`state_root`/`digest` and `parent_hash = H_A` (a placeholder to be finalized after `A`'s hash is computed).
2. Construct header `A` with `parent_hash = hash(B)`.
3. Recompute `B.parent_hash = hash(A)` (two-step fixed-point construction: choose `A`'s other fields freely, compute `hash(A)`, set `B.parent_hash` to it, compute `hash(B)`, set `A.parent_hash` to it — iterate once since neither hash input depends on the other's parent_hash value, so this is a single deterministic construction, not a search).
4. Set `votes_ancestries = [A, B]` in a `GrandpaJustification`, with a `commit` whose precommits target `A.hash()` (or `B.hash()`), and where `base_hash` (lowest-numbered precommit target) is neither `hash(A)` nor `hash(B)`.
5. Wrap this justification (and a `FinalityProof` with `unknown_headers` containing the same two synthetic headers, `block = A.hash()`) inside a `ConsensusMessage::Polkadot` / relay-chain `ConsensusMessage`, encode it as the `proof` in an ISMP `ConsensusMessage`, and submit via `handle_unsigned([Message::Consensus(...)])`.
6. Execution reaches `finality_grandpa::validate_commit` / `headers.ancestry(from, target.hash())`, which loops forever alternating between `hash(A)` and `hash(B)`, hanging the runtime executing the extrinsic.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L65-90)
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
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L109-134)
```rust
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
			// ancestry starts from parent hash but the precommit target hash has been
			// visited
			visited_hashes.insert(signed.precommit.target_hash);
			for hash in route {
				visited_hashes.insert(hash);
			}
		}
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L176-198)
```rust
impl<H: HeaderT> finality_grandpa::Chain<H::Hash, H::Number> for AncestryChain<H>
where
	H::Number: finality_grandpa::BlockNumberOps,
{
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
}
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L69-106)
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

		let mut intermediates = BTreeMap::new();

		// match over the message
		match consensus_message {
			ConsensusMessage::Polkadot(relay_chain_message) => {
				let headers_with_finality_proof = ParachainHeadersWithFinalityProof {
					finality_proof: relay_chain_message.finality_proof,
					parachain_headers: relay_chain_message.parachain_headers,
				};

				let (consensus_state, parachain_headers) =
					verify_parachain_headers_with_grandpa_finality_proof(
						consensus_state,
						headers_with_finality_proof,
					)?;
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L82-87)
```rust
// Max legitimate proof length for a SHA-256 hexary trie: 64 nibbles of trie
// depth (one per hash byte nibble) plus the MSU root. Anything beyond this
// cannot correspond to a real trie path and is rejected to bound verifier
// work and prevent adversarial proofs from driving `nibble_at_depth` past
// the end of the 32-byte key hash.
pub const MAX_PROOF_DEPTH: usize = 65;
```
