### Title
Unbounded ancestry walk in GRANDPA justification verification allows a relayer-supplied header cycle to hang consensus-proof verification - (File: modules/consensus/grandpa/primitives/src/justification.rs)

### Summary
`AncestryChain::ancestry` walks parent-hash pointers over a set of headers (`votes_ancestries`) that are fully attacker-controlled (submitted by any relayer inside a GRANDPA `ConsensusMessage`), with no cycle detection and no bound on the number of hops. This is directly analogous to CVE-2017-6314's `make_available_at_least`: a `while` loop that keeps "succeeding" (finding the next node) on attacker-crafted input without ever reaching its termination condition, causing an unbounded/looping computation instead of a bounded parse.

### Finding Description
`AncestryChain::ancestry` is implemented as: [1](#0-0) 

```
fn ancestry(&self, base: H::Hash, block: H::Hash) -> Result<Vec<H::Hash>, finality_grandpa::Error> {
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

`self.ancestry` is a `BTreeMap<H::Hash, H>` built directly from `votes_ancestries: Vec<H>`, a field of the untrusted `GrandpaJustification` supplied inside the relayer's proof: [2](#0-1) [3](#0-2) 

Because headers are keyed by their own hash and `parent_hash()` is an attacker-chosen field inside each header, a relayer can submit a set of headers `H1 -> H2 -> H3 -> H1` (a cycle) where none of `H1, H2, H3` equals `base`. The loop condition `current_hash != base` never becomes false, and `self.ancestry.get(&current_hash)` keeps returning `Some(...)` for every hop of the cycle, so the loop never hits the `None` branch that would return `Err(NotDescendent)`. The loop runs indefinitely (in a `no_std`/WASM runtime context, this manifests as unbounded execution/looping rather than a clean revert).

This function is invoked directly from `GrandpaJustification::verify_with_voter_set` for every precommit: [4](#0-3) 

and from the top-level verifier used by the ismp-grandpa consensus client: [5](#0-4) 

which is reached by `GrandpaConsensusClient::verify_consensus`, the entry point pallet-ismp calls when any relayer submits a GRANDPA consensus update via an unsigned/permissionless extrinsic: [6](#0-5) 

No caller enforces a maximum on `votes_ancestries.len()` or de-duplicates/validates that the parent-hash chain is acyclic before `ancestry()` is invoked, unlike the BEEFY/Pharos code paths in this same codebase, which the team has already hardened with explicit `MAX_PROOF_DEPTH` bounds against structurally similar issues (e.g. `ProofTooDeep` in `modules/consensus/pharos/primitives/src/spv.rs`).

### Impact Explanation
An unprivileged relayer submitting a GRANDPA consensus proof can construct `votes_ancestries` headers whose `parent_hash` pointers form a cycle that never reaches the precommit's `base_hash`. Verifying that proof drives the node into an unbounded loop. Since GRANDPA consensus verification is on the hot path for accepting new state commitments for Polkadot/Kusama-anchored routes, a relayer or malicious peer can repeatedly submit such proofs to hang/DoS the consensus-verification routine, preventing legitimate consensus updates and message delivery from progressing on that route — a route made unable to deliver messages, one of the accepted impact categories.

### Likelihood Explanation
The `votes_ancestries` field and headers within it are fully controlled by the party that submits the proof — no signature or membership check binds headers in `votes_ancestries` to real, canonically-linked chain state before `ancestry()` walks them; only the precommit's finalized `target_hash`/signatures are separately checked by `finality_grandpa::validate_commit`. Building a small header cycle (as few as 2-3 headers) that hashes correctly is straightforward, since header hashing depends only on the header's own encoded fields (including the attacker-chosen `parent_hash`). This makes the trigger cheap and requires no special privilege — any address able to submit an unsigned/relayed consensus update can attempt it.

### Recommendation
Bound `AncestryChain::ancestry` similarly to the `MAX_PROOF_DEPTH` guards already used elsewhere in this codebase (e.g., Pharos SPV): track visited hashes (e.g., in a `BTreeSet`) and abort with an error once a hash is revisited, and/or cap the number of hops to `votes_ancestries.len() + 1`. This guarantees termination regardless of attacker-supplied header linkage while preserving correct behavior for genuine, acyclic ancestry chains.

### Proof of Concept
1. Relayer constructs three headers `H1`, `H2`, `H3` such that `H1.parent_hash = H2.hash()`, `H2.parent_hash = H3.hash()`, `H3.parent_hash = H1.hash()` (a 3-cycle), none of which equals the honest `base_hash` derived from the lowest-numbered precommit target.
2. Relayer includes `H1, H2, H3` in `GrandpaJustification.votes_ancestries`, and crafts a valid precommit (with a legitimately-signed vote) whose `target_hash` is `H1.hash()` (or any node in the cycle), while `base_hash` is a distinct, unrelated hash not present in the cycle.
3. Submit this as the GRANDPA consensus proof via `GrandpaConsensusClient::verify_consensus` (or directly to `verify_grandpa_finality_proof` / `GrandpaJustification::verify_with_voter_set`).
4. `verify_with_voter_set` calls `ancestry_chain.ancestry(base_hash, H1.hash())`; the loop looks up `H1 -> H2 -> H3 -> H1 -> H2 -> ...` forever since `current_hash` is always found in `self.ancestry` and never equals `base_hash`, hanging verification instead of returning `Err(NotDescendent)`.

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L121-134)
```rust
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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-88)
```rust
	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
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
