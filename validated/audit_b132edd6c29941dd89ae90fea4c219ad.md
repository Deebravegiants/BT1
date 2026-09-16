### Title
Unauthenticated infinite loop in `AncestryChain::ancestry` walk, reachable via GRANDPA consensus proof submission before signature verification - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`verify_grandpa_finality_proof` builds an `AncestryChain` directly from the attacker-supplied `finality_proof.unknown_headers` and calls `AncestryChain::ancestry` **before** the justification's authority signatures are ever checked. `ancestry` walks `parent_hash` pointers in a plain `while current_hash != base` loop with no depth bound and no cycle detection. Because the header set and its `parent_hash` fields are entirely attacker-controlled, a relayer can construct two (or more) headers whose `parent_hash` fields point at each other, forming a cycle that never reaches `base`. The lookup always succeeds (both hashes are in the map), so the loop never returns `Err(NotDescendent)` and spins forever, appending to an ever-growing `route` vector — an unauthenticated, unbounded-loop denial of service triggered purely by malformed input, exactly the bug class described in the OpenJPEG report (malicious input drives the program into an unbounded loop).

### Finding Description
`AncestryChain::ancestry` is implemented as: [1](#0-0) 

It walks `current_hash` back through `self.ancestry` (a `BTreeMap` built straight from the relayer-supplied header list) until it equals `base`, with no maximum iteration count and no visited-set/cycle check.

`AncestryChain::new` builds this map purely from the untrusted `finality_proof.unknown_headers`: [2](#0-1) 

`verify_grandpa_finality_proof` calls `headers.ancestry(...)` **twice**, and both calls happen before `justification.verify(...)` — the only place actual authority signatures are checked: [3](#0-2) 

Because the header contents (including `parent_hash`) are fully attacker-chosen, it is trivial to build two headers `A` and `B` where `hash(A) == B.parent_hash` and `hash(B) == A.parent_hash`, i.e. a genuine 2-cycle. As long as neither hash equals `consensus_state.latest_hash` (`from`/`base`), the `while current_hash != base` loop in `ancestry` toggles between `A` and `B` forever, since both are always found in the map.

This function is reached from the public `ConsensusClient::verify_consensus` entry point that any relayer invokes when submitting a GRANDPA consensus update: [4](#0-3) 

No fee-paying/authenticated relationship or valid signature is required to reach the hang — the crafted `unknown_headers` array is decoded and walked before `justification.verify()` is ever invoked, so even a garbage/self-signed justification (that merely decodes and matches `target_hash`) is sufficient to reach the vulnerable loop.

For comparison, the sibling Pharos SPV verifier explicitly guards against this exact class of bug with a hard `MAX_PROOF_DEPTH` bound checked before any walk: [5](#0-4) 
No equivalent bound exists for the GRANDPA `AncestryChain::ancestry` walk.

### Impact Explanation
Any unprivileged relayer can submit a single consensus-update message that causes the GRANDPA consensus-client verification routine to loop indefinitely (and grow an unbounded `Vec<H256>`), executed synchronously inside pallet call/extrinsic dispatch. This can hang block execution for the runtime processing the consensus update, effectively halting the ISMP consensus pipeline for the affected state machine and freezing all message/proof delivery routed through it — a denial of service against Hyperbridge's core consensus-verification path, satisfying the "route unable to deliver messages" impact criterion.

### Likelihood Explanation
High. The attack requires no privileged role, no valid GRANDPA authority signatures, and no capital — only crafting two headers with mutually-referencing `parent_hash` fields and submitting them as `unknown_headers` in a `ConsensusMessage::StandaloneChain` (or `Relaychain`/`Polkadot`) proof via the standard `verify_consensus` entry point that every relayer already uses.

### Recommendation
Bound `AncestryChain::ancestry` the same way the Pharos SPV verifier bounds its walk: enforce a maximum number of iterations (e.g., `unknown_headers.len() + 1`) and/or track visited hashes, returning `Error::NotDescendent`/`InvalidAncestry` once the bound is exceeded, before performing any ancestry walk — including the ones invoked ahead of `justification.verify()`.

### Proof of Concept
1. Construct header `B` with arbitrary fields; compute `hash(B)`.
2. Construct header `A` with `parent_hash = hash(B)` and other arbitrary fields; compute `hash(A)`.
3. Re-set `B.parent_hash = hash(A)`, forming the cycle `A -> B -> A`.
4. Set `unknown_headers = [A, B]`, `finality_proof.block = hash(target)` where `target` is whichever of `A`/`B` has the higher block number, and supply any justification bytes whose `commit.target_hash` decodes to match `finality_proof.block` (signature validity is irrelevant — it is never reached).
5. Submit this as a `ConsensusMessage::StandaloneChain` (or `Relaychain`) proof through `GrandpaConsensusClient::verify_consensus`.
6. Execution enters `verify_grandpa_finality_proof` → `headers.ancestry(from, target.hash())` → infinite loop in `AncestryChain::ancestry`, hanging the call before signature verification is ever performed.

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L52-93)
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

	// 2. verify justification.
	justification
		.verify(consensus_state.current_set_id, &consensus_state.current_authorities)
		.map_err(|e| Error::JustificationVerify(e.to_string()))?;
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L169-173)
```rust
			ConsensusMessage::StandaloneChain(standalone_chain_message) => {
				let (consensus_state, header, _, _) = verify_grandpa_finality_proof(
					consensus_state,
					standalone_chain_message.finality_proof,
				)?;
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L214-216)
```rust
	if proof_nodes.len() > MAX_PROOF_DEPTH {
		return Err(Error::ProofTooDeep);
	}
```
