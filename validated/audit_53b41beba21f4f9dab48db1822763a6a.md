## Title
Unbounded loop in GRANDPA `AncestryChain::ancestry` allows a single crafted consensus message to hang/OOM validation (DoS) — ([File: modules/consensus/grandpa/primitives/src/justification.rs])

## Summary
Similar to the Rack multipart parser, which never bounds a loop that keeps appending bytes while waiting for a terminator that may never arrive, Hyperbridge's GRANDPA justification verifier contains a loop that walks an attacker-supplied ancestry map until it reaches a target hash — with no cycle detection and no iteration bound. A relayer can submit a single unsigned `handle_unsigned` extrinsic carrying a crafted GRANDPA consensus message whose `votes_ancestries` field encodes a short cycle of headers, causing the loop to run forever while unboundedly growing a `Vec`, exhausting memory/CPU during mempool validation (`validate_unsigned`), which runs for free before any signatures are checked.

## Finding Description
`AncestryChain::ancestry` implements the `finality_grandpa::Chain` trait used to resolve the path between two block hashes over a caller-supplied set of headers: [1](#0-0) 

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

The `ancestry` map is built directly from the untrusted `votes_ancestries: Vec<H>` field of a `GrandpaJustification`: [2](#0-1) [3](#0-2) 

Each header's `hash()` is computed from its own content, but its `parent_hash()` field is an arbitrary attacker-chosen value with no requirement that it correspond to a real chain. An attacker can therefore submit exactly two headers `H1`, `H2` where `H1.parent_hash = H2.hash()` and `H2.parent_hash = H1.hash()`, forming a 2-cycle. If `base` is never equal to either hash, the `while current_hash != base` loop alternates between the two entries forever, pushing to `route` on every iteration with no termination condition and no cap on loop count or vector size.

This function is invoked by `finality_grandpa::validate_commit` before any GRANDPA authority signature is checked: [4](#0-3) 

```rust
let ancestry_chain = AncestryChain::<H>::new(&self.votes_ancestries);
match finality_grandpa::validate_commit(&self.commit, voters, &ancestry_chain) { ... }
```

`validate_commit` uses the `Chain::ancestry` implementation internally to determine ghost/ancestry relationships among precommits — this call happens ahead of `check_message_signature`, which is only invoked later in the loop over `self.commit.precommits`. Consequently, the attacker does not need valid GRANDPA authority signatures to trigger the infinite loop; they only need SCALE-decodable headers and precommits.

This is reachable from an unprivileged relayer through the standard GRANDPA consensus-message path: a `Message::Consensus` is submitted via `pallet_ismp::Call::handle_unsigned`, which pallet-ismp validates for free in `validate_unsigned` by calling `Self::execute`, which in turn dispatches to the GRANDPA consensus client's `verify_grandpa_finality_proof` → `GrandpaJustification::verify_with_voter_set` → the vulnerable `ancestry` call: [5](#0-4) [6](#0-5) 

Since `handle_unsigned` is an unsigned, free extrinsic validated in the transaction pool, this DoS can be triggered by anyone submitting a single crafted transaction, without needing it to ever be included in a block — validation itself hangs or exhausts memory.

## Impact Explanation
An unauthenticated party can submit one crafted (free, unsigned) extrinsic that causes a Hyperbridge parachain node's transaction-pool validation (and any other place `verify_grandpa_finality_proof`/`verify_fraud_proof` is invoked, e.g. fraud-proof verification) to spin in an unbounded loop while growing a `Vec<H::Hash>` without limit. This can hang the validating thread and/or exhaust memory, denying block production/validation service — a network-wide availability impact on any chain relying on the GRANDPA consensus client (e.g., relaychain/parachain finality bridging), which is a High-severity resource-exhaustion condition matching CWE-400, directly analogous to the Rack advisory.

## Likelihood Explanation
High. The only requirements are: (1) the attacker constructs two small SCALE-encodable headers with cross-referencing `parent_hash` fields and packages them as `votes_ancestries` in a `GrandpaJustification`/`FinalityProof`, and (2) submits it as an unsigned `handle_unsigned` extrinsic naming a valid GRANDPA `consensus_state_id`. No cryptographic material, stake, or privileged role is required, and the vulnerable code path executes during `validate_unsigned`, which runs before block inclusion and at negligible cost to the attacker.

## Recommendation
Bound the `ancestry` walk: track visited hashes and abort with `Error::NotDescendent` (or a new bounded-path error) if a hash is revisited, and/or cap the maximum route length to the number of entries in `votes_ancestries` (since a valid ancestry path can never exceed that count). Enforce this bound before calling `finality_grandpa::validate_commit`, and additionally bound `votes_ancestries.len()` against a sane maximum (e.g., mirroring `MAX_PROOF_DEPTH`-style caps used elsewhere in the codebase, such as `modules/consensus/pharos/primitives/src/spv.rs`).

## Proof of Concept
1. Construct headers `H1` and `H2` (any type implementing `HeaderT`, e.g., minimal SCALE-valid substrate headers) such that `H1.parent_hash() == H2.hash()` and `H2.parent_hash() == H1.hash()`.
2. Build a `GrandpaJustification { round, commit, votes_ancestries: vec![H1, H2] }` where `commit.precommits` contains at least one precommit whose `target_hash` equals `H1.hash()` (or `H2.hash()`) — this is used as `block` in the `ancestry` call. Signatures inside `commit.precommits` do not need to verify, since `validate_commit`'s internal ancestry check runs first.
3. Wrap this in a `FinalityProof`/`ConsensusMessage` for an existing GRANDPA `consensus_state_id`, encode as a `Message::Consensus`, and submit as `pallet_ismp::Call::handle_unsigned { messages: vec![message] }` with `ensure_none` origin (unsigned).
4. Observe that `AncestryChain::ancestry` in `modules/consensus/grandpa/primitives/src/justification.rs` enters an infinite loop while `validate_unsigned` processes the transaction, growing `route` unboundedly and hanging/crashing the node's validation thread.

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L65-90)
```rust
	/// Validate the commit and the votes' ancestry proofs.
	pub fn verify_with_voter_set(
		&self,
		set_id: u64,
		voters: &VoterSet<AuthorityId>,
	) -> Result<(), anyhow::Error> {
		use finality_grandpa::Chain;

		let ancestry_chain = AncestryChain::<H>::new(&self.votes_ancestries);

		match finality_grandpa::validate_commit(&self.commit, voters, &ancestry_chain) {
			Ok(ref result) if result.is_valid() => {
				if result.num_duplicated_precommits() > 0 ||
					result.num_invalid_voters() > 0 ||
					result.num_equivocations() > 0
				{
					Err(anyhow!("Invalid commit, found one of `duplicate precommits`, `invalid voters`, or `equivocations` {result:?}"))?
				}
			},
			err => {
				let result = err.map_err(|_| {
					anyhow!("[verify_with_voter_set] Invalid ancestry while validating commit!")
				})?;
				Err(anyhow!("invalid commit in grandpa justification: {result:?}"))?
			},
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

**File:** modules/pallets/ismp/src/lib.rs (L614-625)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;
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
