### Title
Unbounded ancestry-walk loop in GRANDPA `AncestryChain::ancestry` allows attacker-crafted header cycle to hang consensus/fraud-proof verification - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`AncestryChain::ancestry` walks a chain of headers from a target hash back to a base hash by repeatedly following `parent_hash` pointers stored in a `BTreeMap` built entirely from attacker-supplied headers (`votes_ancestries` / `unknown_headers`). The loop has no visited-set / cycle detection, exactly mirroring the OpenMcdf `DirectoryTree.TryGetDirectoryEntry` bug class (CWE-835): a per-step "does this satisfy adjacency" check is present, but nothing prevents the walk from revisiting the same node forever if the attacker crafts a cycle among the sibling/parent links.

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

`self.ancestry` is a `BTreeMap<H::Hash, H>` built directly from the untrusted `votes_ancestries: Vec<H>` field of a `GrandpaJustification`, or from `unknown_headers` inside a `FinalityProof`, both fully controlled by whoever submits the consensus/fraud proof: [2](#0-1) 

Because the map is populated solely from attacker-chosen headers keyed by their own hash, an attacker can submit two (or more) headers `H1`, `H2` where `H1.parent_hash() == hash(H2)` and `H2.parent_hash() == hash(H1)`, forming a cycle that never equals `base`. Since both hashes are always present as map keys, the `while current_hash != base` loop never hits the `None` branch (`NotDescendent`) and never reaches `base` — it spins forever.

This is reached by two production call sites:

1. `GrandpaJustification::verify_with_voter_set`, invoked for every relayed GRANDPA consensus update, calls `ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)` per precommit: [3](#0-2) 

2. `GrandpaConsensusClient::verify_fraud_proof` calls `.ancestry()` directly on `unknown_headers` decoded straight from raw proof bytes, before any cryptographic commit/signature validation is performed: [4](#0-3) 

Both `verify_consensus` and `verify_fraud_proof` are the `ConsensusClient` entry points invoked by pallet-ismp when a relayer submits a consensus message or fraud proof — a single unprivileged dispatched call: [5](#0-4) 

### Impact Explanation
An unprivileged relayer can submit one crafted consensus/fraud-proof extrinsic containing a small set of forged headers whose `parent_hash` fields form a cycle. This drives `AncestryChain::ancestry` into an infinite loop with no panic, no gas/weight-based early exit inside the loop itself, and no way for a caller to recover via `try/catch`/`Result` — the executing thread (validator/collator block-execution or off-chain relayer verification thread) spins forever. This is a permanent denial of service on GRANDPA-based consensus-state and fraud-proof verification, which gates all state-membership/non-membership proofs and message delivery for every state machine tracked by that GRANDPA light client — i.e. a route becomes permanently unable to deliver messages until the node/process is killed and the malicious update is filtered out out-of-band.

### Likelihood Explanation
Likelihood is high: the input is a single relayed extrinsic/message, requires no privileged role, no colluding validator set, and no race condition — just two crafted headers with cyclic `parent_hash` pointers, encoded as `Vec<u8>` and passed to `verify_consensus`/`verify_fraud_proof`. The `verify_fraud_proof` path is the most direct, since `.ancestry()` is invoked before any GRANDPA commit signature check.

### Recommendation
Add cycle/visited-set detection (e.g., a `BTreeSet` of already-visited hashes, or a maximum iteration bound equal to `self.ancestry.len() + 1`) inside `AncestryChain::ancestry`, returning `finality_grandpa::Error::NotDescendent` (or a new "cyclic ancestry" error) as soon as a hash is revisited or the bound is exceeded, mirroring the Brent's-algorithm-style cycle protection referenced in the external report.

### Proof of Concept
1. Craft headers `H1` and `H2` such that `hash(H1) != hash(H2)`, `H1.parent_hash() = hash(H2)`, `H2.parent_hash() = hash(H1)`, neither hash equal to the chosen `base`/`target`.
2. Wrap them into a `GrandpaJustification.votes_ancestries` (or a `FinalityProof.unknown_headers`) with a `commit`/`block` whose precommit target is not directly `base`, forcing a call into `ancestry(base_hash, target_hash)`.
3. Submit as the `proof` bytes to `GrandpaConsensusClient::verify_consensus` (or `verify_fraud_proof` with two such proofs).
4. `AncestryChain::ancestry` loops indefinitely inside `self.ancestry.get(&current_hash)` → `current_hash = parent_hash` → repeat, hanging the executing thread.

### Citations

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L157-167)
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L69-96)
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
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L286-320)
```rust
		let first_headers = AncestryChain::<SubstrateHeader>::new(&first_proof.unknown_headers);
		let first_target = first_proof
			.unknown_headers
			.iter()
			.max_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;

		let second_headers = AncestryChain::<SubstrateHeader>::new(&second_proof.unknown_headers);
		let second_target = second_proof
			.unknown_headers
			.iter()
			.max_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;

		if first_target.hash() != first_proof.block || second_target.hash() != second_proof.block {
			return Err(GrandpaError::FraudProofsDifferentChain.into());
		}

		let first_base = first_proof
			.unknown_headers
			.iter()
			.min_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;
		let first_chain = first_headers
			.ancestry(first_base.hash(), first_target.hash())
			.map_err(|_| GrandpaError::InvalidAncestry)?;

		let second_base = second_proof
			.unknown_headers
			.iter()
			.min_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;
		let second_chain = second_headers
			.ancestry(second_base.hash(), second_target.hash())
			.map_err(|_| GrandpaError::InvalidAncestry)?;
```
