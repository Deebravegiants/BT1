## Title
GRANDPA ancestry-chain walk loops forever on relayer-supplied headers with a cyclic parent hash - (File: modules/consensus/grandpa/primitives/src/justification.rs)

### Summary
`AncestryChain::ancestry` (`modules/consensus/grandpa/primitives/src/justification.rs`) walks from a `block` hash back to a `base` hash by repeatedly looking up `parent_hash()` in a map built from the untrusted `unknown_headers` supplied in a GRANDPA `FinalityProof`. The loop has no iteration bound and no cycle detection: if the attacker-supplied header set contains a cycle (header A's `parent_hash` = B, B's `parent_hash` = A, both present in the map), the `while current_hash != base` loop never terminates, because every lookup succeeds and `base` is never reached.

### Finding Description [1](#0-0) 

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

`AncestryChain` is built directly from `finality_proof.unknown_headers`, a `Vec<H>` of headers whose fields (including `parent_hash`) are entirely attacker-controlled and unvalidated at this point: [2](#0-1) 

Critically, `verify_grandpa_finality_proof` calls this unbounded `ancestry()` walk on the untrusted `unknown_headers` *before* the GRANDPA justification/commit signatures are verified: [3](#0-2) 

So an attacker does not need any valid validator signatures — they only need to submit a `ConsensusMessage` whose `unknown_headers` contain two (or more) headers whose `parent_hash` fields point at each other, forming a cycle that never reaches `consensus_state.latest_hash` (`base`). Every hash in the cycle is present in the `BTreeMap`, so the lookup always succeeds and the loop spins forever.

This is reachable from `GrandpaConsensusClient::verify_consensus`, which decodes the entire `ConsensusMessage` (including `unknown_headers`) straight from caller-supplied `proof: Vec<u8>` bytes with no upstream sanitization of header ancestry: [4](#0-3) 

`verify_consensus` is the standard `ConsensusClient` entry point invoked by pallet-ismp when any relayer submits a consensus update message — a permissionless action available to any unprivileged caller, exactly matching the class of "consensus verification (... GRANDPA ...)" call paths in scope. This mirrors the CVE-2017-6471 bug class: a length/graph field taken from untrusted wire data drives a loop with no termination/bound check, causing an infinite loop from a single malformed message.

### Impact Explanation
A crafted GRANDPA consensus update causes the node/runtime processing it to hang in an unbounded loop while validating the consensus proof. In a Substrate/pallet-ismp execution context this can stall the extrinsic/host executing the update, blocking further GRANDPA-based consensus/state updates for the affected consensus client — i.e., the ISMP route relying on this GRANDPA light client becomes unable to deliver or process further verified messages, a form of permanent denial of service/message-delivery freeze for that route, without requiring any valid validator signatures.

### Likelihood Explanation
Any unprivileged relayer can submit an arbitrary `proof` payload to `verify_consensus`. Constructing two headers whose `parent_hash` fields reference each other (and including them in `unknown_headers`) requires no cryptographic material and no valid GRANDPA signatures, since the vulnerable `ancestry()` walk executes before signature verification. This makes the bug trivially triggerable by any party able to submit a consensus message.

### Recommendation
Bound the `ancestry()` walk by the number of entries in `self.ancestry` (or a fixed maximum), and/or track visited hashes in a `BTreeSet` to detect and reject cycles, returning `Error::NotDescendent` (or a new `CyclicAncestry` error) once the number of hops exceeds `self.ancestry.len()`.

### Proof of Concept
1. Attacker crafts a `ConsensusMessage::Polkadot`/`Standalone` GRANDPA update whose `unknown_headers` contains header `A` with `parent_hash = hash(B)` and header `B` with `parent_hash = hash(A)`, with `A` reported as the max-numbered header (the `target`).
2. Attacker submits this as the `proof` argument to `GrandpaConsensusClient::verify_consensus` via the normal permissionless consensus-update path.
3. `verify_grandpa_finality_proof` builds `AncestryChain` from `unknown_headers` and calls `headers.ancestry(from, target.hash())` before any signature check.
4. Since `A` and `B` only reference each other and neither equals `base` (`consensus_state.latest_hash`), the `while current_hash != base` loop in `ancestry()` alternates between `A` and `B` forever, hanging the call.

### Citations

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-93)
```rust
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
