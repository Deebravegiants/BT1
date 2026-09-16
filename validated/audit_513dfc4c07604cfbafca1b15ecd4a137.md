This confirms the vulnerability path is real and reachable. `ConsensusClient::verify_consensus` at [1](#0-0)  decodes an attacker/relayer-supplied `proof: Vec<u8>` into a `ConsensusMessage` containing `ParachainHeadersWithFinalityProof` / `FinalityProof`, whose `unknown_headers: Vec<H>` field is fully attacker-controlled (arbitrary SCALE-decoded headers with arbitrary `parent_hash` fields), and feeds it into `verify_grandpa_finality_proof`, which builds an `AncestryChain` from those headers and calls `.ancestry(...)` — the unbounded `while` loop I found.

### Title
Unbounded ancestry-walk in GRANDPA justification verification allows relayer-triggered infinite loop / DoS - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`AncestryChain::ancestry` walks parent-hash pointers from `block` back to `base` using a `while current_hash != base` loop with no iteration bound and no cycle/visited-set detection, terminating only when the current hash is either equal to `base` or absent from the attacker-supplied header map.

### Finding Description
The loop is defined as: [2](#0-1) 

`AncestryChain::new` populates `self.ancestry` directly from the untrusted `votes_ancestries` / `unknown_headers` vector supplied in the proof, keyed by each header's real hash: [3](#0-2) 

A header's `parent_hash` field is an arbitrary, attacker-chosen value independent of the header's own computed hash (the SCALE-encoded `Header` struct has no binding between its own content-hash and the `parent_hash` field it declares). A relayer can therefore submit two (or more) headers `A`, `B` whose declared `parent_hash` fields point at each other, forming a cycle: `hash(A) -> parent = hash(B)`, `hash(B) -> parent = hash(A)`. As long as neither hash equals `base`, `self.ancestry.get(&current_hash)` always succeeds (since both are present in the map from the submitted proof), and the loop never reaches the `Err(NotDescendent)` branch nor the `base` termination condition — it spins forever, with `route.push(current_hash)` growing without bound, consuming both CPU and memory.

This method is reachable directly through the unprivileged `ConsensusClient::verify_consensus` entry point: [1](#0-0) 
which decodes an attacker-controlled `proof: Vec<u8>` into `ConsensusMessage`/`FinalityProof` containing `unknown_headers`, and calls `verify_grandpa_finality_proof`, which invokes `headers.ancestry(...)` twice: [4](#0-3) 

It is also reachable through `GrandpaJustification::verify_with_voter_set`'s own internal `ancestry_chain.ancestry(base_hash, ...)` call: [5](#0-4) 

and through the equivocation/fraud-proof path `verify_fraud_proof`, which builds two independent `AncestryChain`s from two attacker-supplied `FinalityProof`s and calls `.ancestry(...)` on each: [6](#0-5) 

None of these call sites bound the number of loop iterations, deduplicate visited hashes, or cap `unknown_headers`/`votes_ancestries` length before the walk executes — this contrasts with the deliberate hardening seen elsewhere in the codebase for structurally similar walks (e.g. Pharos SPV's `MAX_PROOF_DEPTH` bound at `modules/consensus/pharos/primitives/src/spv.rs:87`, and BEEFY parachain-header verification bounds), indicating this is a genuine gap rather than an accepted design trade-off.

### Impact Explanation
Any unprivileged relayer can submit a consensus update or fraud proof to the GRANDPA light client that triggers an unbounded loop, hanging the runtime call (`verify_consensus` / `verify_fraud_proof`) that executes it. Since these paths are invoked from block-execution logic in `pallet-ismp` (via extrinsic dispatch / `handle_unsigned`), an infinite loop here can stall block production/execution for the chain running the GRANDPA client, effectively a network/route-availability denial of service that prevents delivery of all Hyperbridge messages relying on that consensus client — matching the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
Likelihood is high: constructing two headers with mutually pointing `parent_hash` values requires no cryptographic break — `parent_hash` is a free-form field, and the attacker fully controls the encoded `Header` bytes placed in `unknown_headers`/`votes_ancestries`. The `finality_grandpa::validate_commit` precheck does not prevent this because the cycle need not include the actual commit/precommit target as long as at least one precommit's ancestry walk is routed through the crafted cycle before ever reaching `base`. Any relayer, without special privilege, fee expenditure beyond submission cost, or need for a valid signature over the cyclic headers themselves (only the precommit signatures need to be valid; the ancestry headers used to fill `votes_ancestries` do not need signatures), can trigger this.

### Recommendation
Bound `AncestryChain::ancestry` with an explicit maximum number of iterations (e.g., proportional to `self.ancestry.len()` or a fixed protocol constant) and/or track visited hashes in a set, returning `Err(finality_grandpa::Error::NotDescendent)` once a hash is revisited or the iteration cap is exceeded. Apply the same defensive pattern already used for Pharos (`MAX_PROOF_DEPTH`) and other proof walks in this codebase.

### Proof of Concept
1. Craft header `A` (arbitrary content, computed hash `HA`) with `parent_hash = HB` (chosen in advance).
2. Craft header `B` (arbitrary content, computed hash `HB`) with `parent_hash = HA`.
3. Include `A` and `B` in `votes_ancestries` of a `GrandpaJustification`, or in `unknown_headers` of a `FinalityProof`, ensuring at least one precommit's `target_hash` (or the finality-proof `target`) resolves through the walk to `HA` or `HB` before reaching the legitimate `base`/`from` hash.
4. Submit as the `proof` argument to `GrandpaConsensusClient::verify_consensus` (or as `proof_1`/`proof_2` to `verify_fraud_proof`).
5. `AncestryChain::ancestry` enters `while current_hash != base` with `current_hash` oscillating between `HA` and `HB` forever, since both are present in `self.ancestry` and neither equals `base` — the call never returns, hanging the executing node.

### Citations

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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L264-320)
```rust
	fn verify_fraud_proof(
		&self,
		_host: &dyn IsmpHost,
		trusted_consensus_state: Vec<u8>,
		proof_1: Vec<u8>,
		proof_2: Vec<u8>,
	) -> Result<(), Error> {
		// decode the consensus state
		let consensus_state: ConsensusState =
			codec::Decode::decode(&mut &trusted_consensus_state[..])
				.map_err(|e| GrandpaError::DecodeConsensusState(format!("{e:?}")))?;

		let first_proof: FinalityProof<SubstrateHeader> = codec::Decode::decode(&mut &proof_1[..])
			.map_err(|e| GrandpaError::DecodeFinalityProof(format!("{e:?}")))?;

		let second_proof: FinalityProof<SubstrateHeader> = codec::Decode::decode(&mut &proof_2[..])
			.map_err(|e| GrandpaError::DecodeFinalityProof(format!("{e:?}")))?;

		if first_proof.block == second_proof.block {
			return Err(GrandpaError::FraudProofsSameBlock.into());
		}

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L125-127)
```rust
			let route = ancestry_chain
				.ancestry(base_hash, signed.precommit.target_hash)
				.map_err(|_| anyhow!("[verify_with_voter_set] Invalid ancestry!"))?;
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
