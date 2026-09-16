### Title
Unbounded/Quadratic Ancestry-Chain Traversal in GRANDPA Justification Verification Enables Compute-DoS on Consensus Updates - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`GrandpaJustification::verify_with_voter_set` calls `AncestryChain::ancestry()` once per precommit in the submitted justification, and each call re-walks the shared ancestor chain from the vote's target hash back to a common `base_hash` following `parent_hash()` pointers with no depth limit and no memoization. Both the number of precommits and the length of the ancestry chain (`votes_ancestries`) are attacker-controlled fields of the untrusted `ConsensusMessage`/`FinalityProof` submitted by any relayer. Because many precommits can target distinct headers that all share the same long ancestry prefix (a "reused nesting path", directly analogous to the pypdf outline re-use issue), the verifier repeats the same O(L) walk once per validator vote, giving O(V·L) work for a proof whose size is only O(V+L).

### Finding Description
`AncestryChain::ancestry` in [1](#0-0)  performs a pointer-chasing walk from `block` to `base` using a `BTreeMap<Hash, Header>` built directly from the untrusted `votes_ancestries: Vec<H>` field of the `GrandpaJustification` ( [2](#0-1) , [3](#0-2) ). There is no cap on `votes_ancestries.len()` and no cap on the chain length walked per call.

In `verify_with_voter_set`, this function is invoked **once per precommit** in `self.commit.precommits` ( [4](#0-3) ):
```
for signed in self.commit.precommits.iter() {
    ...
    let route = ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)...
    ...
}
```
Both `precommits` (bounded only by the authority-set size, which can be in the hundreds/thousands) and `votes_ancestries` (bounded only by the extrinsic/consensus-message payload size) are supplied by the caller inside `ConsensusMessage`/`FinalityProof`, decoded and passed straight into `verify_grandpa_finality_proof` in [5](#0-4) , which is reachable by any relayer through `ConsensusClient::verify_consensus` in [6](#0-5) .

An attacker can craft a justification where many (up to authority-set-size) precommits target distinct headers that all sit along one shared, maximal-length `votes_ancestries` chain. Every one of these targets forces a full independent O(L) traversal of the same shared prefix (the "reused nesting path"), yielding O(V·L) total work from an O(V+L)-sized payload — a classic algorithmic-complexity blow-up, the same bug class as the pypdf outline-traversal CVE (CWE-405/CWE-834): the cost is driven by re-walking shared/nested structure repeatedly rather than by the raw size of the input.

Note: because header hashes are cryptographic, a literal infinite loop/cycle in the chain is not feasible (would require a hash pre-image/fixed point), so this is a super-linear compute-amplification issue rather than non-termination — but it still lets a bounded-size proof consume disproportionate CPU relative to its size/weight.

### Impact Explanation
`verify_consensus` for the GRANDPA client is on the direct message-verification path that ultimately updates trusted consensus state and unlocks message/state-proof delivery for all downstream ISMP consumers (relayers, token bridges, intent settlement) anchored to that consensus client. A relayer that can submit a crafted `ConsensusMessage` with maximal `precommits`/`votes_ancestries` can force the runtime to spend CPU proportional to `V·L` instead of `V+L` while paying weight/fees calibrated to the smaller, linear cost model (if the pallet's benchmarked weight for `verify_consensus`/`submit`-type extrinsics does not already account for the quadratic term). This is a resource-exhaustion / block-time-consumption vector reachable from a single dispatched extrinsic, matching the "long runtimes/large memory usage" class described in the referenced advisory, rather than a memory-safety or fund-theft bug per se.

### Likelihood Explanation
Medium. The attack requires the attacker to construct a genuine, correctly-hash-linked ancestry chain of many headers (not merely crafted field values, since header hashes must actually chain) and gather (or fabricate, if signature checks on precommits are satisfiable by equivocating/duplicate signers are otherwise filtered) enough distinct precommit targets — feasible for anyone able to submit a `ConsensusMessage` extrinsic, without needing any authority-set collusion beyond what's already required for a valid-looking justification skeleton. The actual amplification factor is bounded by extrinsic size limits and authority-set size, so the practical severity depends on the parachain's configured max extrinsic length and authority set size, which is why this is rated Medium rather than High/Critical.

### Recommendation
- Cap `votes_ancestries.len()` and `precommits.len()` to sane maxima enforced before calling `verify()`/`verify_with_voter_set` (mirroring the `MAX_PROOF_DEPTH` pattern already applied in `modules/consensus/pharos/primitives/src/spv.rs`).
- Memoize/cache the ancestry walk so that repeated queries sharing a prefix reuse previously computed routes instead of re-walking them per precommit, turning the worst case back to O(V+L).
- Re-benchmark the GRANDPA `verify_consensus` weight to account for the worst-case `V·L` traversal cost, or reject proofs whose `precommits.len() * votes_ancestries.len()` exceeds a configured bound.

### Proof of Concept
Conceptual (not executed against a live chain):
1. Build a legitimate-looking `votes_ancestries` chain of `L` headers `H_1 → H_2 → … → H_L` where each `H_i.parent_hash() == hash(H_{i+1})` (fully attacker-constructible since header contents, not just parent_hash, are free-form and hashes are computed forward, not inverted).
2. Construct `V` precommits (up to authority-set size) whose `target_hash` values are `hash(H_1), hash(H_2), …, hash(H_V)` (i.e., distinct points along the same shared chain), each carrying a validly-signed precommit message from a distinct authority (or the maximum number the attacker can obtain/forge under the existing signature-check path).
3. Submit this as a `GrandpaJustification` inside a `ConsensusMessage` via the ISMP GRANDPA consensus client's `verify_consensus`.
4. `verify_with_voter_set` will call `ancestry_chain.ancestry(base_hash, target_hash)` once per precommit, each re-walking up to `L` map lookups, for total work ≈ `V·L`, while the submitted payload size is only ≈ `V+L`.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L41-48)
```rust
pub struct GrandpaJustification<H: HeaderT> {
	/// Current voting round number, monotonically increasing
	pub round: u64,
	/// Contains block hash & number that's being finalized and the signatures.
	pub commit: Commit<H>,
	/// Contains the path from a [`PreCommit`]'s target hash to the GHOST finalized block.
	pub votes_ancestries: Vec<H>,
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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L161-167)
```rust
impl<H: HeaderT> AncestryChain<H> {
	/// Initialize the ancestry chain given a set of relay chain headers.
	pub fn new(ancestry: &[H]) -> AncestryChain<H> {
		let ancestry: BTreeMap<_, _> = ancestry.iter().cloned().map(|h: H| (h.hash(), h)).collect();

		AncestryChain { ancestry }
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L125-184)
```rust

					let state_id: StateMachine = match T::Coprocessor::get() {
						Some(StateMachine::Polkadot(_)) => StateMachine::Polkadot(para_id),
						Some(StateMachine::Kusama(_)) => StateMachine::Kusama(para_id),
						_ => Err(GrandpaError::CoprocessorNotSet)?,
					};

					for header in header_vec {
						let digest_result =
							fetch_overlay_root_and_timestamp(header.digest(), slot_duration)?;

						let height: u32 = (*header.number()).into();

						let intermediate = match T::Coprocessor::get() {
							Some(id) if id == state_id => StateCommitmentHeight {
								// for the coprocessor, we only care about the child root & mmr root
								commitment: StateCommitment {
									timestamp: digest_result.timestamp,
									overlay_root: Some(digest_result.ismp_digest.mmr_root),
									state_root: digest_result.ismp_digest.child_trie_root, /* child root */
								},
								height: height.into(),
							},
							_ => StateCommitmentHeight {
								commitment: StateCommitment {
									timestamp: digest_result.timestamp,
									overlay_root: Some(digest_result.ismp_digest.child_trie_root),
									state_root: header.state_root,
								},
								height: height.into(),
							},
						};

						state_commitments_vec.push(intermediate);
					}

					intermediates.insert(
						StateMachineId { state_id, consensus_state_id },
						state_commitments_vec,
					);
				}

				Ok((consensus_state.encode(), intermediates))
			},
			ConsensusMessage::StandaloneChain(standalone_chain_message) => {
				let (consensus_state, header, _, _) = verify_grandpa_finality_proof(
					consensus_state,
					standalone_chain_message.finality_proof,
				)?;

				let slot_duration = SupportedStateMachines::<T>::get(consensus_state.state_machine)
					.ok_or(GrandpaError::SlotDurationNotSet(consensus_state.state_machine))?;
				let digest_result =
					fetch_overlay_root_and_timestamp(header.digest(), slot_duration)?;

				let height: u32 = (*header.number()).into();

				let state_id = consensus_state.state_machine;

				let intermediate = StateCommitmentHeight {
```
