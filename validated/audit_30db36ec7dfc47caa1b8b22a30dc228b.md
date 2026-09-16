## Title
Unbounded ancestry-cycle walk in GRANDPA `AncestryChain::ancestry` allows a relayer-submitted consensus proof to hang the ISMP consensus client - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`AncestryChain::ancestry` walks parent-hash pointers taken directly from attacker-controlled `unknown_headers` supplied in a GRANDPA `ConsensusMessage`, with no acyclicity check. `verify_grandpa_finality_proof` — invoked from `GrandpaConsensusClient::verify_consensus`, itself reachable from any unprivileged relayer submitting a Consensus message through pallet-ismp — calls this function on every submission. This is structurally the same bug class as CVE-2023-20197: a loop whose termination condition ("did we reach `base`?") can be defeated by attacker-supplied structured input, leading to CPU exhaustion / non-termination on a single crafted submission.

### Finding Description
`AncestryChain::new` builds a `BTreeMap<Hash, Header>` straight from `finality_proof.unknown_headers`, which is fully attacker-controlled (submitted as part of the `ConsensusMessage`/`FinalityProof` payload): [1](#0-0) 

The `ancestry` walk then repeatedly follows `parent_hash()` links until it finds `base`: [2](#0-1) 

Crucially, headers are keyed in the map by their own real (Blake2/BlakeTwo256) hash, but the `parent_hash` **field inside a header is an arbitrary, attacker-chosen value** that is never checked against the actual parent's real content beyond being looked up by that value in the map. Nothing prevents a submitter from crafting two (or more) headers A and B such that `A.parent_hash == hash(B)` and `B.parent_hash == hash(A)`. Once inserted into the `ancestry` `BTreeMap` (keyed by their real hashes), calling `ancestry(base, block)` where the walk enters this A↔B cycle — and `base` is never one of the cycle members — causes the `while current_hash != base` loop to iterate forever, since both `current_hash` values remain present in the map at every step and neither ever equals `base`.

This function is called unconditionally, twice per `verify_grandpa_finality_proof` invocation (once conditionally for the "already-finalized" base check, once unconditionally for `from -> target.hash()`): [3](#0-2) [4](#0-3) 

`verify_grandpa_finality_proof` (and `verify_parachain_headers_with_grandpa_finality_proof`, which calls it internally) is exactly the function `GrandpaConsensusClient::verify_consensus` calls for every `ConsensusMessage` variant (`StandaloneChain`, `Polkadot`, `Relaychain`): [5](#0-4) [6](#0-5) 

`verify_consensus` is the standard `ConsensusClient` entry point invoked when a relayer submits a consensus update message on-chain — this is a normal, unprivileged, permissionless action any relayer can take (the same category of caller ISMP relies on for consensus updates generally, analogous to `handle_unsigned`/unsigned message dispatch paths elsewhere in the codebase, e.g. the call-decompressor's unsigned `decompress_call` path).

There is no check anywhere in `verify_grandpa_finality_proof`, `AncestryChain::new`, or `AncestryChain::ancestry` that the supplied `unknown_headers` form an acyclic, well-ordered chain before the ancestry walk is performed — the cycle is only ever detected implicitly by non-termination, never rejected explicitly.

### Impact Explanation
An attacker submits a crafted `ConsensusMessage` (any variant using `verify_grandpa_finality_proof`) whose `unknown_headers` contain a small parent-hash cycle unrelated to `base`/`from`. When the node processes this message during consensus verification, the `ancestry` call enters an infinite loop, hanging the thread executing consensus verification. Because this code path runs inside block-import / extrinsic execution wherever the GRANDPA consensus client verifies proofs, this can stall processing for the runtime/relayer node handling the update — a denial of service against the GRANDPA consensus route, preventing further consensus updates and message delivery to/from that route ("a route unable to deliver messages"), matching the acceptance criteria. This is a High-severity availability bug, directly analogous to the ClamAV HFS+ decompression completion-check bug that let an unauthenticated attacker hang the scanning process.

### Likelihood Explanation
Likelihood is high: constructing two headers with matching mutual `parent_hash` fields requires no special privilege or knowledge — the headers only need to decode successfully as `SubstrateHeader`/`H: HeaderT` and be included in `unknown_headers`; their `parent_hash` fields are free-form attacker input not checked against real chain ancestry before the walk. Any relayer able to submit a `ConsensusMessage` (the standard consensus-update path) can trigger this with a single crafted message.

### Recommendation
- Before performing the `ancestry` walk, validate that `unknown_headers` forms a strictly monotonic, cycle-free chain by block number (e.g., require each header's number to be strictly less than the one that names it as parent, or bound the number of `ancestry.get` lookups by `unknown_headers.len()` and error out if exceeded).
- Track visited hashes during the `while` loop in `AncestryChain::ancestry` and return `Err(finality_grandpa::Error::NotDescendent)` immediately if a hash is revisited, guaranteeing termination within `unknown_headers.len()` iterations regardless of attacker-crafted cycles.

### Proof of Concept
1. Construct header `B` (a `DefaultHeader`) with arbitrary content, and compute `hash(B)`.
2. Construct header `A` with `parent_hash = hash(B)`, compute `hash(A)`.
3. Reconstruct/rewrite `B` (or a further header) with `parent_hash = hash(A)`, so the pair mutually references each other, and include both in `finality_proof.unknown_headers` alongside enough other headers to satisfy `min_by_key`/`max_by_key` (`base`, `target`) not equal to either A or B.
4. Submit this as `ConsensusMessage::StandaloneChain` (or `Relaychain`/`Polkadot`) to `GrandpaConsensusClient::verify_consensus`.
5. Ensure the ancestry route from `from`/`base` to `target.hash()` is constructed such that the walk enters the A↔B cycle before reaching `base` — the call to `headers.ancestry(from, target.hash())` in `verify_grandpa_finality_proof` (`modules/consensus/grandpa/verifier/src/lib.rs:88`) never terminates, hanging the calling thread/block-execution indefinitely.

### Citations

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-88)
```rust
	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L102-106)
```rust
				let (consensus_state, parachain_headers) =
					verify_parachain_headers_with_grandpa_finality_proof(
						consensus_state,
						headers_with_finality_proof,
					)?;
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L169-173)
```rust
			ConsensusMessage::StandaloneChain(standalone_chain_message) => {
				let (consensus_state, header, _, _) = verify_grandpa_finality_proof(
					consensus_state,
					standalone_chain_message.finality_proof,
				)?;
```
