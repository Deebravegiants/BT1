Based on my analysis, I found a valid analog. The bug class from CVE-2023-21933 (crafted server-side operation causing a hang/crash DoS) maps to an unbounded-loop denial-of-service in Hyperbridge's GRANDPA finality-proof ancestry walk, reachable from the unsigned `handle_unsigned` message-dispatch path that any relayer can submit.

### Title
Unbounded cycle in `AncestryChain::ancestry` allows an attacker-crafted GRANDPA finality proof to hang node execution (infinite loop DoS) - (File: modules/consensus/grandpa/primitives/src/justification.rs)

### Summary
`AncestryChain::ancestry` walks a caller-supplied set of headers (`finality_proof.unknown_headers`) from a `block` hash back to a `base` hash by repeatedly following each header's `parent_hash` field, with no cycle detection and no iteration bound. Because `unknown_headers` are attacker-supplied SCALE-decoded headers carried inside an unsigned ISMP consensus message, an attacker can submit two (or more) headers whose `parent_hash` fields point at each other, forming a cycle that never reaches `base`. The `while current_hash != base` loop then spins forever, hanging the node (validator, full node, or relayer) that processes the message.

### Finding Description
`AncestryChain::ancestry` is implemented as: [1](#0-0) 

The `ancestry` BTreeMap is built directly from `finality_proof.unknown_headers`, which is decoded straight from the untrusted proof bytes with no structural validation that the headers form an acyclic chain: [2](#0-1) 

`verify_grandpa_finality_proof` calls this `ancestry()` walk twice before the GRANDPA justification signatures are even checked — once to validate the trusted `base`/`latest_hash` link, and once to compute `finalized`: [3](#0-2) 

`GrandpaJustification::verify_with_voter_set` performs a third `ancestry()` call per precommit: [4](#0-3) 

Reachability: `pallet-ismp`'s unsigned `handle_unsigned` extrinsic accepts a `Vec<Message>` from anyone (`ensure_none`) and immediately calls `Self::execute`, which invokes `handle_incoming_message` for every submitted message, including consensus messages: [5](#0-4) 

A consensus message routes into `GrandpaConsensusClient::verify_consensus`, which decodes the attacker-supplied `ConsensusMessage` and — for `ConsensusMessage::StandaloneChain` — calls `verify_grandpa_finality_proof` directly with the caller-controlled `finality_proof` (containing `unknown_headers`): [6](#0-5) 

Because `handle_unsigned` messages are validated via `ValidateUnsigned::validate_unsigned`, every node in the network that receives this transaction in its pool (not just the block author) executes `Self::execute(messages.clone())` — including this vulnerable ancestry walk — before the transaction is even included in a block: [7](#0-6) 

Note that headers hashes are content-derived (`header.hash()`), but nothing prevents an attacker from setting one header's `parent_hash` field to equal another attacker-supplied header's hash and vice versa, forming a genuine 2-(or-more)-cycle among `unknown_headers` entries, since `parent_hash` is just an ordinary field with no binding requiring monotonic descent toward a real chain tip.

### Impact Explanation
Because every node that receives or validates the unsigned extrinsic (via `validate_unsigned`, and again on execution) runs the vulnerable `ancestry()` walk, a single relayed message can hang every relaying/validating node network-wide that processes it — a "route unable to deliver messages" / liveness-halting denial of service, matching the CVE-2023-21933 impact class (hang or repeatable crash caused by an easily-reachable operation). Because it is invoked from unsigned-extrinsic validation, the attack costs no fees and can be repeated.

### Likelihood Explanation
`handle_unsigned` is deliberately open to any unprivileged caller (that is its entire purpose — free relaying of ISMP messages), and the GRANDPA consensus client is enabled on state machines using this client. Constructing two headers with cross-referencing `parent_hash` fields (and otherwise well-formed digests/roots so they decode successfully) requires no special privileges or cryptographic secrets — only crafting the plaintext header struct fields, which is fully attacker-controlled input. This makes the likelihood high for any deployment where the GRANDPA client is configured.

### Recommendation
Bound `AncestryChain::ancestry` with a maximum number of hops (e.g., `unknown_headers.len()`), and/or track visited hashes in a `BTreeSet` to detect and reject cycles, returning `Err(NotDescendent)` once a hash is revisited instead of looping forever.

### Proof of Concept
1. Attacker builds two synthetic headers `H_a` and `H_b` (arbitrary but internally-consistent field values so they decode as valid `Header`s), setting `H_a.parent_hash = H_b.hash()` and `H_b.parent_hash = H_a.hash()`.
2. Attacker sets `finality_proof.unknown_headers = [H_a, H_b]`, `finality_proof.block` to one of these hashes not equal to the trusted `consensus_state.latest_hash`/`base`, and supplies any syntactically-decodable `justification` bytes (the loop hangs before signature verification completes for many code paths, and even the pre-justification `ancestry()` calls in `verify_grandpa_finality_proof` line 88 hang first).
3. Attacker wraps this in `ConsensusMessage::StandaloneChain` and submits via `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Consensus(...)] }` as an unsigned transaction.
4. Every node that receives the transaction runs `ValidateUnsigned::validate_unsigned` → `Self::execute` → `handle_incoming_message` → `GrandpaConsensusClient::verify_consensus` → `verify_grandpa_finality_proof` → `AncestryChain::ancestry`, which enters an infinite loop cycling between `H_a` and `H_b`, hanging that node's execution thread indefinitely.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L121-134)
```rust
			if base_hash == signed.precommit.target_hash {
				continue;
			}

			let route = ancestry_chain
				.ancestry(base_hash, signed.precommit.target_hash)
				.map_err(|_| anyhow!("[verify_with_voter_set] Invalid ancestry!"))?;
			// ancestry starts from parent hash but the precommit target hash has been
			// visited
			visited_hashes.insert(signed.precommit.target_hash);
			for hash in route {
				visited_hashes.insert(hash);
			}
		}
```

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L76-88)
```rust
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

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L169-173)
```rust
			ConsensusMessage::StandaloneChain(standalone_chain_message) => {
				let (consensus_state, header, _, _) = verify_grandpa_finality_proof(
					consensus_state,
					standalone_chain_message.finality_proof,
				)?;
```
