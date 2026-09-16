## Title
Infinite loop in GRANDPA `AncestryChain::ancestry` walk via cyclic parent-hash headers in an unsigned consensus proof - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`GrandpaConsensusClient::verify_consensus` decodes an attacker-supplied `FinalityProof` whose `unknown_headers: Vec<H>` field is an unbounded, uncycle-checked list of headers [1](#0-0) . Before any signature/justification check is performed, the verifier builds an `AncestryChain` from these headers and calls `.ancestry(...)` twice to compute the route between hashes [2](#0-1) . `AncestryChain::ancestry` walks `current_hash -> parent_hash` in a `while` loop that only terminates by hitting `base` or by a missing map entry [3](#0-2) . Because the map is populated purely from attacker-supplied header content (`h.hash()` -> `h`, with `parent_hash` also attacker-controlled bytes), an attacker can submit headers forming a cycle that is reachable from the walk's starting hash but never reaches `base`, causing an unbounded loop.

### Finding Description
`FinalityProof<H>` carries `unknown_headers: Vec<H>` with no upper bound, no cycle check, and no exclusion of self-referential/duplicate parent hashes [1](#0-0) .

`AncestryChain::new` simply indexes the supplied headers by `h.hash()`:
```rust
let ancestry: BTreeMap<_, _> = ancestry.iter().cloned().map(|h: H| (h.hash(), h)).collect();
``` [4](#0-3) 

`ancestry()` then walks parent links:
```rust
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
``` [5](#0-4) 

Since `parent_hash()` is just a field read from an attacker-crafted `H` (the header's own `hash()` is a hash of its own encoded fields, and its `parent_hash` field is an independent, freely settable value), an attacker can craft two headers `H1`, `H2` where `H1.parent_hash = H2.hash()` and `H2.parent_hash = H1.hash()`. Both are inserted into the `BTreeMap` under their own hash. If the walk's starting hash lands on this 2-cycle and `base` is not one of the cycle members, `self.ancestry.get(&current_hash)` will always return `Some(...)` for members of the cycle, `current_hash` will bounce between `H1.hash()` and `H2.hash()` forever, and the loop never terminates (mirrors CVE‑2018‑1338's infinite-loop-on-crafted-node-graph pattern).

This walk is invoked in `verify_grandpa_finality_proof` *before* the justification/signature is verified:
```rust
if base.number() < &consensus_state.latest_height {
    headers.ancestry(base.hash(), consensus_state.latest_hash).map_err(|_| Error::InvalidAncestry)?;
}
let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
...
justification.verify(...)  // happens after
``` [6](#0-5) 

`verify_grandpa_finality_proof` is the core of `GrandpaConsensusClient::verify_consensus`, which is the standard `ConsensusClient::verify_consensus` entry point reached from a submitted (unsigned) consensus proof via pallet-ismp/ismp-grandpa [7](#0-6) . Any unprivileged relayer can submit a crafted `ConsensusMessage`/`FinalityProof` through this path.

### Impact Explanation
This causes a permanent liveness failure ("route unable to deliver messages") of the GRANDPA-tracked chain: the block/extrinsic that dispatches the malicious consensus proof through `handle_unsigned`/consensus-update path spins forever inside the runtime for every node that executes/validates it, effectively halting block production/finality for the ISMP host (or at minimum burning the transaction's execution slot indefinitely, well beyond any expected weight, since the CPU-bound loop is not itself weight-metered per iteration). Because the check runs before signature verification, the attacker does not need a valid GRANDPA justification, just self-consistent, syntactically valid headers with a cyclic `parent_hash` graph — this is a low-cost, unauthenticated DoS against consensus updates for any GRANDPA-based state machine tracked by the host.

### Likelihood Explanation
High. `unknown_headers` is a plain `Vec<H>` decoded via SCALE with no bound, and forming two headers with reciprocal `parent_hash` fields requires no cryptographic work (parent_hash is just an opaque field, not independently verified until much later, if at all, in this code path). Any account able to submit a consensus proof (the standard permissionless relayer flow) can trigger it.

### Recommendation
- Bound `unknown_headers` (e.g. `BoundedVec` with a sane max length) as already done for `epoch_header_ancestry` in the BSC client.
- Make `AncestryChain::ancestry` cycle-safe: track visited hashes and bail with an error once `route.len()` exceeds `unknown_headers.len()` (or once a hash is revisited), instead of relying solely on reaching `base`.
- Reject `unknown_headers` containing duplicate hashes or cycles at construction time (`AncestryChain::new`), before any walk is attempted.

### Proof of Concept
1. Craft header `H1` with `parent_hash = keccak/blake2(H2_bytes)` and header `H2` with `parent_hash = keccak/blake2(H1_bytes)` (both otherwise well-formed SCALE-decodable headers so `Header::hash()` succeeds).
2. Set `finality_proof.unknown_headers = vec![H1, H2, ..., real_target_header]` such that `target = max_by_key(number)` is some other real header whose `hash()` equals `finality_proof.block`, and ensure the walk starting hash (`from` = `consensus_state.latest_hash`, or `base.hash()`) resolves into the `H1`/`H2` cycle rather than reaching `base` directly.
3. Submit this `ConsensusMessage` through the standard unsigned consensus-update extrinsic path to `GrandpaConsensusClient::verify_consensus`.
4. Observe `verify_grandpa_finality_proof` -> `AncestryChain::ancestry` never returns, hanging the runtime call that processes the extrinsic.

### Citations

**File:** modules/consensus/grandpa/primitives/src/lib.rs (L58-66)
```rust
#[derive(Debug, PartialEq, Encode, Decode, Clone)]
pub struct FinalityProof<H: codec::Codec> {
	/// The hash of block F for which justification is provided.
	pub block: Hash,
	/// Justification of the block F.
	pub justification: Vec<u8>,
	/// The set of headers in the range (B; F] that we believe are unknown to the caller. Ordered.
	pub unknown_headers: Vec<H>,
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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L161-167)
```rust
impl<H: HeaderT> AncestryChain<H> {
	/// Initialize the ancestry chain given a set of relay chain headers.
	pub fn new(ancestry: &[H]) -> AncestryChain<H> {
		let ancestry: BTreeMap<_, _> = ancestry.iter().cloned().map(|h: H| (h.hash(), h)).collect();

		AncestryChain { ancestry }
	}
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L180-198)
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
}
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
