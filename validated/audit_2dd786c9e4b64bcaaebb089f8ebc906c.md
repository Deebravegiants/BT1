### Title
Unauthenticated Denial of Service via Infinite Loop in GRANDPA `AncestryChain::ancestry` Header Walk (Cyclic `unknown_headers`) - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic executes attacker-supplied consensus messages for free (no signature, no fee) both when gossiped through the transaction pool (`validate_unsigned`) and when included in a block. For GRANDPA consensus clients, this ultimately calls `verify_grandpa_finality_proof`, which walks an attacker-controlled header ancestry (`AncestryChain::ancestry`) **before** the GRANDPA justification signature is ever checked. Because the `parent_hash` field of each header in `unknown_headers` is fully attacker-controlled and unauthenticated at that point, an attacker can submit two or more crafted headers whose `parent_hash` fields point to each other, forming a cycle. The `ancestry()` walk has no cycle/visited-set detection and no iteration bound, so it loops forever, hanging the calling node's CPU — exactly analogous to SimpleJWT's unbounded, pre-authentication PBKDF2 iteration count driven by an untrusted `p2c` header.

### Finding Description
`AncestryChain::ancestry` walks parent hashes from `block` back to `base`: [1](#0-0) 

The map (`self.ancestry`) is built directly from the untrusted `unknown_headers` supplied in the `FinalityProof`, with no validation that the headers form an acyclic, terminating chain: [2](#0-1) 

`verify_grandpa_finality_proof` invokes this walk from the trusted `consensus_state.latest_hash` (`from`) to the attacker-chosen `target.hash()` **before** `justification.verify(...)` is called — i.e., before any cryptographic authentication of the proof: [3](#0-2) 

Because each header's `parent_hash` field is arbitrary attacker-chosen content (not cryptographically bound to an actual parent until this very check), an attacker can construct two headers `A` and `B` such that `A.parent_hash == hash(B)` and `B.parent_hash == hash(A)` (fixed-point construction, no hash inversion required — pick `B`'s content first, hash it, set that as `A.parent_hash`, hash `A`, set that as `B.parent_hash`). Neither hash equals the trusted `from`/`base` hash, so the `while current_hash != base` loop never terminates: `self.ancestry.get(&current_hash)` always succeeds (bouncing between `A` and `B`), and the equality check against `base` never holds. The loop runs indefinitely with no CPU/step bound.

This is reachable through the unsigned, feeless `handle_unsigned` extrinsic call path, which is executed both during mempool/`validate_unsigned` (checked by every full node that receives the gossiped transaction) and on execution: [4](#0-3) [5](#0-4) 

The GRANDPA ismp client wrapper decodes and dispatches to `verify_grandpa_finality_proof` for `ConsensusMessage`s carried in these unsigned messages, and `verify_fraud_proof` similarly builds two independent `AncestryChain`s and calls `.ancestry(...)` on attacker-supplied header sets before any signature check: [6](#0-5) 

### Impact Explanation
This directly matches "a route unable to deliver messages": any full node processing the crafted unsigned `handle_unsigned`/`ConsensusMessage` transaction — including simply validating it in the transaction pool before block inclusion — enters an unbounded loop and hangs. Since `handle_unsigned` is explicitly designed to let *anyone* submit consensus proofs for free ("execute the provided batch of ISMP messages for free with valid proofs"), an unauthenticated attacker can broadcast such a transaction to every relayer/full node on the network, causing denial of service to the GRANDPA-bridged state machine (and potentially destabilizing the whole node if the tx-pool validation thread/worker blocks), without any authentication, signature, or fee cost. This satisfies the "Medium/High/Critical" and "route unable to deliver messages" criteria.

### Likelihood Explanation
High. The attack requires only constructing two SCALE-encoded headers with mutually-referencing `parent_hash` fields — a trivial, purely off-chain computation with no cryptographic hardness. No signatures, no privileged role, and no fee are required since `handle_unsigned` is an unsigned extrinsic validated for free by `validate_unsigned`, which is exactly the entry point evaluated by every peer node during gossip/mempool admission.

### Recommendation
- Add a hard iteration/visited-set bound to `AncestryChain::ancestry` (e.g., track visited hashes and error out on revisit, and/or cap the walk length to `unknown_headers.len()`), rejecting cyclic or otherwise non-terminating ancestry chains before doing any work.
- Consider validating that `unknown_headers` forms a strictly monotonically-decreasing-by-number, single, acyclic chain up front (as it already computes `min_by_key`/`max_by_key` on `number()`), rejecting any header set with a `parent_hash` reference cycle prior to entering the walk.
- Apply the same bound to all call sites that build an `AncestryChain` from untrusted proof data, including `verify_fraud_proof` in `modules/ismp/clients/grandpa/src/consensus.rs`.

### Proof of Concept
1. Construct header `B` with arbitrary content (number, state_root, digest) and compute `hash(B)`.
2. Construct header `A` with `A.parent_hash = hash(B)`, then compute `hash(A)`.
3. Set `B.parent_hash = hash(A)`, finalizing the 2-cycle `A <-> B`.
4. Build a `FinalityProof` with `unknown_headers = [A, B]`, `block = hash(A)` (so `target = A`, since it's picked by `max_by_key(number)` — set `A.number` highest), and any syntactically valid (but not necessarily cryptographically correct) `justification` bytes that decode successfully and whose `commit.target_hash == hash(A)`.
5. Wrap this in a `ConsensusMessage`/`Message::Consensus` and submit it via `pallet_ismp::Call::handle_unsigned { messages: vec![...] }` as an unsigned transaction.
6. Any node validating this transaction calls `verify_grandpa_finality_proof`, which calls `headers.ancestry(consensus_state.latest_hash, hash(A))`; since `hash(A)` and `hash(B)` never equal `consensus_state.latest_hash`, and both are present in the ancestry map, the `while current_hash != base` loop toggles between `A` and `B` forever, hanging the node before `justification.verify(...)` is ever reached.

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L74-93)
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

	// 2. verify justification.
	justification
		.verify(consensus_state.current_set_id, &consensus_state.current_authorities)
		.map_err(|e| Error::JustificationVerify(e.to_string()))?;
```

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
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
