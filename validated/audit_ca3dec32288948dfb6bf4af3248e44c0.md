### Title
Unbounded cycle in GRANDPA `AncestryChain::ancestry` walk causes infinite loop / DoS on consensus proof submission - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
The GRANDPA consensus verifier's ancestry-walking routine, `AncestryChain::ancestry`, walks backwards from a target header to a base header purely by following each header's `parent_hash` field inside an attacker-supplied `unknown_headers` set, with no depth bound and no cycle detection. Because both the header's own hash and its `parent_hash` are attacker-controlled values inside a submitted consensus proof, a relayer can craft two (or more) headers whose `parent_hash` fields point at each other, forming a closed cycle. When the walk's starting hash falls into that cycle instead of ever reaching the required `base`, the `while current_hash != base` loop never terminates and never fails, spinning forever and consuming host/relayer or node CPU indefinitely — a resource-exhaustion condition analogous to the `SitemapLoader` infinite-recursion CVE (self-referencing input driving an unbounded traversal with no depth guard).

### Finding Description
`AncestryChain::ancestry` is implemented as: [1](#0-0) 

```rust
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

`self.ancestry` is a `BTreeMap<H::Hash, H>` built directly from the caller-supplied `unknown_headers: Vec<H>` in `AncestryChain::new`: [2](#0-1) 

Both the header hash (map key, from `h.hash()`) and each header's `parent_hash()` field are fully attacker-controlled, since `unknown_headers` is decoded straight from the submitted `FinalityProof`/`ParachainHeadersWithFinalityProof` message. Nothing in `verify_grandpa_finality_proof` restricts `unknown_headers` to a genuine acyclic chain before calling `.ancestry(...)`: [3](#0-2) 

An attacker can submit two headers `A` and `B` where `A.parent_hash == hash(B)` and `B.parent_hash == hash(A)`, both included in `unknown_headers`. If `target` (max-by-number header) or any header on the walk from `target`/`base` falls into this 2-cycle rather than reaching `base` directly, `current_hash` will oscillate `hash(A) -> hash(B) -> hash(A) -> ...` forever: it is always found in the map (`Some`), so the function never returns `Err(NotDescendent)`, and it never equals `base`, so the loop condition never becomes false. This differs from the honest case where an unrelated/malformed ancestry immediately hits a hash absent from the map and returns an error quickly — here the loop is permanently self-sustaining.

This is the exact bug class described in the external report: an unbounded traversal driven by attacker input that references itself, with no depth/visited-set guard, causing the process to hang/consume resources indefinitely. Note that other proof-verification paths in this same repository (e.g., the Pharos SPV trie walker) were explicitly hardened with `MAX_PROOF_DEPTH` bounds and comments about bounding attacker-controlled sibling paths — no equivalent guard exists for the GRANDPA `AncestryChain::ancestry` walk.

### Impact Explanation
`verify_grandpa_finality_proof` is invoked from the permissionless GRANDPA `ConsensusClient::verify_consensus` implementation, which is reachable by any unprivileged relayer submitting a GRANDPA consensus update through `pallet-ismp`'s `handle_unsigned`/consensus dispatch path (the same class of entry point called out in scope: "consensus verification ... pallet-ismp handle_unsigned"). A single malicious consensus-proof submission containing a small number of cyclically self-referencing headers in `unknown_headers` can cause the runtime/host executing verification to spin in an infinite loop. Because this runs inside block/extrinsic execution (or validate_unsigned/relayer verification logic), this can stall or hang the executing node/relayer process, denying availability of the GRANDPA-based state-machine route — matching "a route unable to deliver messages" per the validation criteria. This is a Medium-severity availability/DoS issue (CWE-400/CWE-674 analog), not a fund-theft or forgery bug.

### Likelihood Explanation
The construction requires only crafting two headers with cross-referencing `parent_hash` fields and packaging them as `unknown_headers` in a `FinalityProof` — no valid GRANDPA signatures are needed to trigger the loop, because the ancestry walk (`headers.ancestry(...)`) is performed in `verify_grandpa_finality_proof` before/independently of the point where `justification.verify(...)` cryptographically checks the commit signatures in some call orders (note: `ancestry` on `from -> target` happens at line 88, prior to the `justification.verify` call at line 91-93 in `verify_grandpa_finality_proof`). This means the hang can be triggered without needing a valid supermajority signature over the malicious header set, only crafted header content, making it cheap and reproducible for any relayer able to submit an unsigned/less-trusted consensus message.

### Recommendation
Bound the `AncestryChain::ancestry` walk by the size of the input header set (e.g. iterate at most `self.ancestry.len()` steps) or track visited hashes in a `BTreeSet` and return `Err(NotDescendent)` immediately upon revisiting a hash, mirroring the `MAX_PROOF_DEPTH` style guards already used elsewhere in the codebase (e.g. Pharos SPV proof walking). Additionally, validate that `unknown_headers` forms a genuine acyclic ancestry chain (each header's `parent_hash` strictly decreasing in `number()`, or a visited-set check) before calling `.ancestry()`, so malformed/cyclic proofs are rejected cheaply rather than causing unbounded looping.

### Proof of Concept
Conceptual PoC (not runnable without the crate's test harness, but describes the exact construction):
1. Construct header `A` with `A.number = 10`, `A.parent_hash = hash(B)`.
2. Construct header `B` with `B.number = 11`, `B.parent_hash = hash(A)`.
3. Construct header `Target` with `Target.number = 12`, `Target.parent_hash = hash(A)` (or `hash(B)`), matching `finality_proof.block`.
4. Submit `FinalityProof { block: hash(Target), justification: <any decodable justification whose commit.target_hash == hash(Target)>, unknown_headers: vec![A, B, Target] }` via the GRANDPA consensus dispatch path.
5. In `verify_grandpa_finality_proof`, `headers.ancestry(from, target.hash())` (or the `base`-to-`consensus_state.latest_hash` check at lines 82-86) walks `Target -> A -> B -> A -> B -> ...` indefinitely, since `A` and `B`'s hashes are both present in the `AncestryChain` map and neither ever equals `base`/`from`. [4](#0-3)

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L74-88)
```rust
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
```
