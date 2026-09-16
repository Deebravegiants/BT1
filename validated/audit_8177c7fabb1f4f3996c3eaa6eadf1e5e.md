### Title
Unbounded ancestry walk in GRANDPA `AncestryChain::ancestry` can infinite-loop on a cyclic header set supplied via an untrusted consensus proof - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`AncestryChain::ancestry` walks from a target block hash back to a base hash by repeatedly looking up `parent_hash` in a `BTreeMap` built directly from the relayer-supplied `unknown_headers` list, with no visited-set/cycle check and no maximum iteration bound. [1](#0-0) 
This mirrors the pypdf `TreeObject` bug class (CWE-835, GHSA-996q-pr4m-cvgq): a parent/child graph is traversed by following pointers without loop detection, so an attacker-controlled cyclic structure can drive the traversal into an infinite loop.

### Finding Description
`AncestryChain::new` builds the ancestry index purely from the caller-supplied header list, keyed by each header's own hash: [2](#0-1) 
`AncestryChain::ancestry(base, block)` then loops `while current_hash != base`, following `parent_hash()` through the map until either `base` is reached or the hash is missing from the map:
```
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
``` [3](#0-2) 

`unknown_headers` is untrusted, attacker-crafted data submitted as part of a `FinalityProof` before any of it has been validated against a genuine relay chain: `verify_grandpa_finality_proof` builds `AncestryChain::<H>::new(&finality_proof.unknown_headers)` and immediately calls `.ancestry(...)` on it, prior to verifying the actual GRANDPA justification/signatures for those headers: [4](#0-3) 

Since each header's hash is derived from its own encoded contents (number, parent_hash, state_root, extrinsics_root, digest), an attacker can construct two or more synthetic headers `A` and `B` whose `parent_hash` fields point at each other (`A.parent_hash = hash(B)`, `B.parent_hash = hash(A)`), forming a genuine 2-hash cycle in the `BTreeMap`. If the `ancestry()` walk starting at `target.hash()` enters this cycle without ever reaching `base_hash` (e.g., `base` is some header not on the cycle, or absent altogether), `current_hash` will oscillate between `hash(A)` and `hash(B)` forever — `self.ancestry.get(&current_hash)` always returns `Some`, so the `None` branch that would terminate the loop is never taken, and the loop condition `current_hash != base` never becomes false.

This differs from the `verify()` method's usage of `ancestry_chain.ancestry(base_hash, target_hash)` after `finality_grandpa::validate_commit` has already validated real GRANDPA votes — but `verify_grandpa_finality_proof` itself calls `headers.ancestry(from, target.hash())` and `headers.ancestry(base.hash(), consensus_state.latest_hash)` **before** `justification.verify(...)` is invoked: [5](#0-4) 
so the cyclic, unvalidated header set is walked prior to any cryptographic check that would reject forged headers.

### Impact Explanation
This is reachable by any relayer submitting a GRANDPA consensus update (an unsigned/dispatched message processed by `pallet-ismp`'s consensus-client update path, ultimately invoking `verify_grandpa_finality_proof`). A relayer needs no special privilege to submit a crafted `ParachainHeadersWithFinalityProof`/`FinalityProof`. Triggering the infinite loop inside the runtime (on-chain execution context, `no_std`) hangs block execution / the extrinsic that processes the consensus update, which is a denial-of-service against the GRANDPA light client route used for parachain header finalization and downstream ISMP message delivery — effectively making that route unable to deliver messages until intervention (e.g., a runtime upgrade or forced restart), which satisfies "a route unable to deliver messages."

### Likelihood Explanation
Medium-to-High: constructing two headers whose `parent_hash` fields point at each other requires only computing hashes of self-crafted `Header` structs (all fields, including `parent_hash`, are attacker-controlled in the submitted proof) — no cryptographic break is needed, since the cycle is checked before the justification signature is verified. The only prerequisite is that the crafted `target`/`base` selection from `unknown_headers` (max/min by block number) routes the ancestry walk through the cyclic pair rather than terminating immediately, which is achievable by controlling the `number()` field of the injected headers.

### Recommendation
Add cycle detection (a `visited: BTreeSet<H::Hash>` checked/inserted on each iteration, erroring out if a hash repeats) and/or a hard iteration bound (e.g., bounded by `unknown_headers.len()`, since a valid acyclic ancestry chain can never need more steps than there are headers) inside `AncestryChain::ancestry` before dereferencing `parent_hash()` further. Apply the same bound/cycle check to any other ancestry-walk-style loop reachable from unvalidated proof data.

### Proof of Concept
1. Craft two `Header` structs `A` and `B` (arbitrary body, e.g., default extrinsics/state roots) such that `A.parent_hash = B.hash()` and `B.parent_hash = A.hash()` (feasible since header hash covers only `A`'s own fields, not `B`'s, so the two hashes can be fixed independently and then embedded as each other's `parent_hash`).
2. Submit these as part of `finality_proof.unknown_headers` in a `ParachainHeadersWithFinalityProof`/`FinalityProof` message such that `target` (max by number) resolves to `A` or `B`, and `base`/`consensus_state.latest_hash` is any hash not equal to `A.hash()` or `B.hash()` and not present in the map.
3. Call `verify_grandpa_finality_proof` (as invoked from the on-chain consensus-client update extrinsic). The call `headers.ancestry(from, target.hash())` at [6](#0-5)  enters `AncestryChain::ancestry`, which will loop forever between `A` and `B` since `current_hash` is always found in `self.ancestry` and never equals `base`.

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
