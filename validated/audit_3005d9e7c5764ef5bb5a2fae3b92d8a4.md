### Title
GRANDPA ancestry-chain traversal loops forever on attacker-supplied cyclic headers - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
The ALPINE-CVE-2026-44777 bug class is unbounded recursion/traversal with no cycle detection when two nodes (jq modules) reference each other. Hyperbridge's GRANDPA consensus verifier contains the same class of bug: `AncestryChain::ancestry` walks a `parent_hash` chain built entirely from attacker-supplied, unverified headers, with no cycle detection and no bound on the number of hops walked.

### Finding Description
`AncestryChain::ancestry` walks backwards from a `block` hash to a `base` hash by repeatedly looking up `parent_hash` in a `BTreeMap` built from the caller-supplied header set, with no visited-set/cycle check: [1](#0-0) 

This map is built directly from `finality_proof.unknown_headers`, a `Vec<H>` that is fully attacker-controlled — it is decoded straight out of the submitted consensus proof with no relationship constraints between entries beyond what `ancestry()` itself later checks: [2](#0-1) 

Each `SubstrateHeader` is a plain SCALE-decoded struct (`number`, `parent_hash`, `state_root`, `extrinsics_root`, `digest`) — `parent_hash` is not constrained to be a hash of any real block, so an attacker can freely choose two headers `H1`, `H2` such that `H1.parent_hash == hash(H2)` and `H2.parent_hash == hash(H1)`, forming a 2-cycle, and additionally craft a `target` header whose `parent_hash` points into that cycle.

This structure is reachable from `verify_grandpa_finality_proof`, which is invoked by `GrandpaConsensusClient::verify_consensus` on every submitted GRANDPA consensus message (an unprivileged, unsigned/relayed extrinsic path): [3](#0-2) [4](#0-3) 

`headers.ancestry(from, target.hash())` walks from `target` toward the trusted `from` hash (the previously stored `consensus_state.latest_hash`, which is *not* part of the attacker-supplied header set). If the walk enters the attacker-crafted cycle before ever reaching `from`, every subsequent lookup in the while-loop of `ancestry()` succeeds (`Some(current_header)`), so `current_hash` never equals `base`/`from` and the loop never terminates and never errors — it spins forever appending to `route`.

The identical unbounded-traversal pattern also exists in `GrandpaJustification::verify_with_voter_set`, which calls `ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)` using `self.votes_ancestries` — likewise a raw, attacker-controlled `Vec<H>` decoded from the justification bytes embedded in the same proof: [5](#0-4) 

This mirrors the jq CVE exactly: a graph-like structure built from untrusted, mutually-referencing entries is traversed with no cycle detection, causing the traversal to never terminate.

### Impact Explanation
This is reachable by any relayer/party able to submit a GRANDPA consensus update message to `pallet-ismp` (an unprivileged, permissionless action). A crafted proof containing a two-node cycle in either `unknown_headers` or `votes_ancestries` causes `verify_consensus` to enter an infinite loop during on-chain execution of the extrinsic. Because Substrate's weight metering does not pre-empt CPU-bound loops mid-execution, this can consume the entire block's execution time (or exhaust memory via the ever-growing `route` vector), stalling block production / halting the parachain's consensus-update path — a denial of service against a core Hyperbridge component (route unable to deliver messages, since consensus updates for a route can no longer be processed). This satisfies "Medium" severity per the CVSS vector class (availability-only, no confidentiality/integrity impact), matching the reference advisory's rating.

### Likelihood Explanation
High: no privileged access is required. The attacker only needs to craft SCALE-encoded headers with arbitrary `parent_hash` fields (trivial, since headers are not required to correspond to real chain blocks in this untrusted vector) and submit them as part of a GRANDPA `ConsensusMessage` via the normal message-submission path.

### Recommendation
Bound `AncestryChain::ancestry` with an explicit iteration/visited-set cycle check: track visited hashes in a `BTreeSet` and return an error (e.g. `Error::AncestryCycle`) if a hash is revisited, or cap the number of hops to at most `unknown_headers.len()` (since a valid, cycle-free ancestry chain can visit each supplied header at most once). Apply the same fix to both call sites (`verify_grandpa_finality_proof`/`verify_parachain_headers_with_grandpa_finality_proof` and `GrandpaJustification::verify_with_voter_set`).

### Proof of Concept
1. Construct two `SubstrateHeader`s `H1`, `H2` with arbitrary `state_root`/`extrinsics_root`/`digest`, setting `H1.parent_hash = hash(H2)` and `H2.parent_hash = hash(H1)` (no preimage constraints needed since `parent_hash` is an independent field).
2. Construct a `target` header with `number` greater than all others and `parent_hash = hash(H1)`, and a `base`/min-number header unrelated to the cycle.
3. Build `FinalityProof { block: hash(target), justification: <valid-looking GrandpaJustification bytes>, unknown_headers: vec![H1, H2, target, base] }` and wrap it in `ConsensusMessage::Relaychain(...)` per `modules/ismp/clients/grandpa/src/messages.rs`. [6](#0-5) 
4. Submit this as the `proof` argument to `GrandpaConsensusClient::verify_consensus` (via the normal consensus-update extrinsic). `verify_grandpa_finality_proof` calls `headers.ancestry(consensus_state.latest_hash, target.hash())`, which walks `target -> H1 -> H2 -> H1 -> H2 -> ...` indefinitely since neither `H1` nor `H2` equals `consensus_state.latest_hash` and both are always found in the map, causing the runtime to spin in the `while current_hash != base` loop shown at [7](#0-6)  indefinitely.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L66-134)
```rust
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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L161-174)
```rust
impl<H: HeaderT> AncestryChain<H> {
	/// Initialize the ancestry chain given a set of relay chain headers.
	pub fn new(ancestry: &[H]) -> AncestryChain<H> {
		let ancestry: BTreeMap<_, _> = ancestry.iter().cloned().map(|h: H| (h.hash(), h)).collect();

		AncestryChain { ancestry }
	}

	/// Fetch a header from the ancestry chain, given it's hash. Returns [`None`] if it doesn't
	/// exist.
	pub fn header(&self, hash: &H::Hash) -> Option<&H> {
		self.ancestry.get(hash)
	}
}
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

**File:** modules/ismp/clients/grandpa/src/messages.rs (L26-48)
```rust
#[derive(Clone, Debug, Encode, Decode)]
pub enum ConsensusMessage {
	/// This is the variant representing the standalone chain
	StandaloneChain(StandaloneChainMessage),
	/// This is the variant representing the Polkadot relay chain
	Polkadot(RelayChainMessage),
	/// This is the variant representing a standalone relaychain
	Relaychain(RelayChainMessage),
}

#[derive(Clone, Debug, Encode, Decode)]
pub struct StandaloneChainMessage {
	/// finality proof
	pub finality_proof: FinalityProof<SubstrateHeader>,
}

#[derive(Clone, Debug, Encode, Decode)]
pub struct RelayChainMessage {
	/// finality proof
	pub finality_proof: FinalityProof<SubstrateHeader>,
	/// parachain headers
	pub parachain_headers: BTreeMap<H256, ParachainHeaderProofs>,
}
```
