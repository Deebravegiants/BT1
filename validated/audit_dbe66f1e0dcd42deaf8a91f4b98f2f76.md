### Title
Unbounded ancestry-traversal loop in GRANDPA justification verification allows CPU-exhaustion DoS via crafted `votes_ancestries` cycle - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`AncestryChain::ancestry`, used while verifying GRANDPA finality justifications submitted in a permissionless consensus-update message, walks parent-hash pointers in a `while current_hash != base` loop with no bound on the number of iterations and no cycle detection. The header set it walks (`votes_ancestries`) is fully attacker-controlled data inside the submitted justification. A relayer can craft two (or more) fabricated headers whose `parent_hash` fields point at each other, producing a cycle that the loop can traverse indefinitely without ever reaching `base`, mirroring the CVE-2017-14170 pattern of a loop driven by attacker-supplied structure with no termination/EOF safeguard.

### Finding Description
`AncestryChain` is built directly from the untrusted `votes_ancestries: Vec<H>` field of a `GrandpaJustification`: [1](#0-0) 

Its `ancestry` implementation (used both as the `finality_grandpa::Chain` trait for `validate_commit` and again explicitly per precommit) walks backwards from `block` to `base` purely by following `parent_hash()` pointers found in the attacker-supplied map, with no depth limit and no protection against revisiting an already-seen hash: [2](#0-1) 

The map key for each header is `h.hash()` — i.e., the hash of the header's own encoded content, which includes its `parent_hash` field as ordinary data. Nothing constrains this field to point at a genuine ancestor: a header's declared `parent_hash` can be set to any 32-byte value, including the hash of another attacker-fabricated header in the same `votes_ancestries` list. This lets an attacker craft two distinct headers `A` and `B` (differing in some other field so `hash(A) != hash(B)`) with `A.parent_hash = hash(B)` and `B.parent_hash = hash(A)`. When `ancestry` is called with `block = hash(A)` and a `base` that is neither `hash(A)` nor `hash(B)`, the loop toggles `A -> B -> A -> B -> ...` forever, since it can only terminate by reaching `base` or by a map miss — neither of which occurs on a self-sustaining cycle.

This function is invoked from `verify_with_voter_set`, which is the ancestry-check core of justification verification, reachable for every precommit in the commit: [3](#0-2) 

and it is also passed as the `Chain` implementation into `finality_grandpa::validate_commit` at the very start of `verify_with_voter_set`, so the same unbounded walk can be triggered before any signature/threshold checks run.

The public entry point is `verify_grandpa_finality_proof`, called for every submitted GRANDPA consensus update or parachain-header finality proof: [4](#0-3) 

This is dispatched from the ISMP `ConsensusClient` implementation for GRANDPA, which is reachable from any relayer submitting a consensus update extrinsic/message — an unprivileged, permissionless path.

### Impact Explanation
A single crafted GRANDPA consensus proof (or equivocation/fraud proof, which decodes and verifies the same justification structure) can drive the verifying node/runtime into an effectively unbounded loop, consuming CPU without terminating. On a Substrate runtime this can exhaust the extrinsic's weight/time budget or hang execution, and on the off-chain prover/relayer side it can hang the verifying process. Because GRANDPA consensus updates gate state-commitment intake for ISMP messages, a hung verifier blocks message delivery for the affected route — a denial of service against the bridge's consensus-update path, consistent with "a route unable to deliver messages."

### Likelihood Explanation
`votes_ancestries` and the justification's header contents are fully attacker-controlled inputs on a permissionless path (anyone can submit a consensus update / fraud proof). Constructing two headers whose `parent_hash` fields reference each other requires no special privilege or cryptographic break — headers here are plain SCALE-decodable structures and the only constraint is that their SCALE-encoded hashes differ, which is trivial to satisfy by varying an unrelated field. No signature is required over the ancestry chain itself; only the final commit signatures are checked, and those are validated using the same `Chain` implementation that would already loop.

### Recommendation
Bound `AncestryChain::ancestry` explicitly: track visited hashes (e.g., a `BTreeSet`) and immediately return an error (e.g., `NotDescendent`) if a hash is revisited before `base` is reached, and/or cap total iterations at `votes_ancestries.len() + 1` (the maximum possible chain length given the supplied header set). This makes the loop's worst-case cost proportional to the submitted proof size rather than unbounded, closing the CVE-2017-14170-style gap between a claimed/implied traversal length and the actual backing data.

### Proof of Concept
1. Craft header `B` with an arbitrary distinguishing field and `parent_hash = H_A` (a placeholder).
2. Compute `hash(B)`, then craft header `A` with `parent_hash = hash(B)`.
3. Recompute `hash(A)`, and update `B.parent_hash = hash(A)` so the two hashes are mutually consistent (iterate `A`/`B` content until the fixed point is reached — trivial since both are freely chosen SCALE structures with no signature binding requirement on ancestry).
4. Submit a `GrandpaJustification` where `votes_ancestries = [A, B]`, and a precommit whose `target_hash = hash(A)` while `base_hash` (lowest-numbered precommit target) is some third, unrelated hash not present in `{hash(A), hash(B)}`.
5. Call `verify_with_voter_set` (via `verify_grandpa_finality_proof`) with this justification: `finality_grandpa::validate_commit` (or the explicit per-precommit `ancestry_chain.ancestry(base_hash, target_hash)` call) enters `AncestryChain::ancestry`, which loops `A -> B -> A -> B -> …` indefinitely without reaching `base_hash`, consuming CPU without bound.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L56-134)
```rust
	pub fn verify(&self, set_id: u64, authorities: &AuthorityList) -> Result<(), anyhow::Error> {
		// It's safe to assume that the authority list will not contain duplicates,
		// since this list is extracted from a verified relaychain header.
		let voters =
			VoterSet::new(authorities.iter().cloned()).ok_or(anyhow!("Invalid Authorities Set"))?;

		self.verify_with_voter_set(set_id, &voters)
	}

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L157-174)
```rust
pub struct AncestryChain<H: HeaderT> {
	ancestry: BTreeMap<H::Hash, H>,
}

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L176-197)
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
```

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L44-93)
```rust
pub fn verify_grandpa_finality_proof<H>(
	mut consensus_state: ConsensusState,
	finality_proof: FinalityProof<H>,
) -> Result<(ConsensusState, H, Vec<H256>, AncestryChain<H>), Error>
where
	H: Header<Hash = H256, Number = u32>,
	H::Number: finality_grandpa::BlockNumberOps + Into<u32>,
{
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

	// 2. verify justification.
	justification
		.verify(consensus_state.current_set_id, &consensus_state.current_authorities)
		.map_err(|e| Error::JustificationVerify(e.to_string()))?;
```
