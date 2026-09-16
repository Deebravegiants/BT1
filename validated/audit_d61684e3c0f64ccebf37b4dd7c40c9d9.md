## Title
Unbounded ancestry-walk loop in GRANDPA finality-proof verification allows free unsigned extrinsics to hang/OOM every full node - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`AncestryChain::ancestry` (used by both `GrandpaJustification::verify` and `verify_grandpa_finality_proof`) walks a `BTreeMap<Hash, Header>` built entirely from attacker-supplied `unknown_headers` before any cryptographic signature or authority-set check is performed. The walk has no depth bound and no cycle detection. Since the header set is caller-controlled, a submitter can construct two (or more) headers whose `parent_hash` fields reference each other, forming a cycle that never reaches the `base`/`from` target hash. `pallet-ismp`'s `handle_unsigned` is validated for *free*, by *any unsigned submitter*, in every node's transaction-pool `validate_unsigned` hook, so this proof-of-work-free computation happens on every node in the network before proofs are otherwise rejected.

### Finding Description
`verify_grandpa_finality_proof` builds an `AncestryChain` straight from the untrusted `finality_proof.unknown_headers` and immediately calls `headers.ancestry(from, target.hash())` **before** calling `justification.verify(...)`: [1](#0-0) 

`AncestryChain::ancestry` walks backward via `parent_hash` lookups in a map keyed by header hash, with no depth limit and no protection against a cycle: [2](#0-1) 

Because headers are attacker-controlled data (only their hash needs to be internally consistent with their own encoded content, which any submitter can freely choose), it is trivial to construct header `A` with `parent_hash = hash(B)` and header `B` with `parent_hash = hash(A)`, neither of which chains to the trusted `base`/`from` hash. When `ancestry()` walks from such a header, `current_hash` will alternate between `hash(A)` and `hash(B)` forever — the loop condition `current_hash != base` never becomes false, and the lookup never returns `None` (since both hashes are present in the map), so the function never returns. This same code path is shared by `GrandpaJustification::verify`'s per-precommit ancestry walk.

This proof structure is submitted as part of an ISMP `Message::Consensus` for the GRANDPA consensus client (registered in production runtimes, per `parachain/runtimes/gargantua/src/weights/ismp_grandpa.rs` and `parachain/runtimes/nexus/src/weights/ismp_grandpa.rs`), and dispatched via `pallet_ismp::Call::handle_unsigned`, which is explicitly documented as executing "for free" as an unsigned extrinsic and is validated by every node's `ValidateUnsigned::validate_unsigned`: [3](#0-2) 

Unlike the BEEFY path — where Gargantua's `IsmpCallFilter` explicitly rejects raw `handle_unsigned` batches carrying BEEFY consensus messages, requiring SP1 zkVM verification instead — the filter only checks for the BEEFY consensus id and does not block GRANDPA: [4](#0-3) 

No length bound on `unknown_headers` or cycle-guard exists anywhere in the GRANDPA verifier/primitives crates (unlike the Pharos SPV verifier, which explicitly caps `MAX_PROOF_DEPTH` and rejects over-deep proofs — see `modules/consensus/pharos/primitives/src/spv.rs`). The GRANDPA path has no analogous protection.

### Impact Explanation
Since `validate_unsigned` runs in every node's transaction pool before block inclusion, and the call carries no fee (unsigned, free execution), an attacker can submit a single crafted consensus message and force every full node/collator on the network to hang in an infinite loop (or accumulate an unbounded `route` Vec, risking memory exhaustion) during mempool validation. This is a network-wide denial of service reachable from a single unauthenticated transaction — matching the CWE-400/CWE-20 class of the reference Next.js advisory, but here affecting the base layer's transaction-validation path rather than an HTTP server.

### Likelihood Explanation
High. Constructing two headers with mutually-referencing `parent_hash` values requires no privileged information — headers are opaque byte blobs whose fields (including `parent_hash`) are chosen by the submitter; only their own hash needs to be internally self-consistent (which is automatic, since the hash is a pure function of the encoded content). No signatures need to be forged to reach the vulnerable code, since the ancestry walk executes *before* `justification.verify()` is called.

### Recommendation
Bound `AncestryChain::ancestry` with an explicit maximum iteration count (equal to, e.g., `unknown_headers.len()`), and/or track visited hashes and abort with an error the first time a hash is revisited, instead of looping until `base` is reached or a `None` lookup occurs. Apply the same depth-limit discipline already used in the Pharos SPV verifier (`MAX_PROOF_DEPTH`) to the GRANDPA ancestry walk before it is exposed to any unsigned/free-of-charge path.

### Proof of Concept
1. Construct header `A` with an arbitrary chosen `parent_hash = H(B_encoded)` and other fields as desired; construct header `B` with `parent_hash = H(A_encoded)`.
2. Set `finality_proof.unknown_headers = [A, B]`, `finality_proof.block = A.hash()` (satisfying `target.hash() == finality_proof.block`), and craft `justification.commit.target_hash = A.hash()` (SCALE-decodable, signature check is never reached).
3. Submit `pallet_ismp::Call::handle_unsigned { messages: [Message::Consensus(...)] }` referencing the GRANDPA consensus state id as an unsigned extrinsic.
4. Every node's `ValidateUnsigned::validate_unsigned` calls `Self::execute(messages)` → GRANDPA client's `verify_consensus` → `verify_grandpa_finality_proof` → `headers.ancestry(from, target.hash())`, which enters the `A ↔ B` cycle and never returns, hanging the node's transaction-pool validation thread indefinitely.

*(Note: I could not execute this PoC or fully confirm the exact SCALE encoding requirements for a minimal reproducer within this session; the control-flow and reachability analysis above is based on direct reading of `justification.rs`, `verifier/src/lib.rs`, `pallets/ismp/src/lib.rs`, and the Gargantua/Nexus runtime registrations of the GRANDPA client.)*

### Citations

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L52-90)
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
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L157-198)
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

	/// Fetch a header from the ancestry chain, given it's hash. Returns [`None`] if it doesn't
	/// exist.
	pub fn header(&self, hash: &H::Hash) -> Option<&H> {
		self.ancestry.get(hash)
	}
}

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

**File:** modules/pallets/ismp/src/lib.rs (L614-626)
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

**File:** parachain/runtimes/gargantua/src/lib.rs (L818-836)
```rust
pub struct IsmpCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for IsmpCallFilter {
	fn contains(call: &RuntimeCall) -> bool {
		use ::ismp::{host::IsmpHost, messaging::Message};
		match call {
			RuntimeCall::Ismp(pallet_ismp::Call::fund_message { .. }) => false,
			RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned { messages }) => {
				let host = Ismp::default();
				!messages.iter().any(|message| match message {
					Message::Consensus(consensus) =>
						host.consensus_client_id(consensus.consensus_state_id) ==
							Some(ismp_beefy::BEEFY_CONSENSUS_ID),
					_ => false,
				})
			},
			_ => true,
		}
	}
}
```
