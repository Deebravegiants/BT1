### Title
Unbounded/cyclic ancestry-chain walk in GRANDPA finality-proof verification allows unauthenticated CPU-exhaustion DoS - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`AncestryChain::ancestry` walks a `parent_hash` chain built entirely from attacker-supplied, unsigned header bytes (`finality_proof.unknown_headers`) *before* any cryptographic signature is checked. Because the walk only terminates when it hits the target `base` hash or a hash absent from the attacker-controlled map, a submitter can construct a closed cycle of fabricated headers that never reaches `base`, causing an infinite loop. This is reachable from the unsigned, fee-less `pallet_ismp::handle_unsigned` extrinsic — including during `validate_unsigned` mempool validation that every full node performs on every gossiped transaction — making it a zero-cost, network-wide CPU-exhaustion analog to CVE-2017-1000476 (`ReadDDSInfo`'s unchecked loop count from untrusted input).

### Finding Description
`AncestryChain::ancestry` is implemented as: [1](#0-0) 

The `ancestry: BTreeMap<H::Hash, H>` map is built directly from `finality_proof.unknown_headers`, a `Vec<H>` of SCALE-decoded headers supplied wholesale by the caller with no structural or cryptographic validation: [2](#0-1) 

`verify_grandpa_finality_proof` calls `headers.ancestry(...)` twice — once for the "unbonded gap" check and once to compute `finalized` — and both calls happen **before** `justification.verify(...)` is invoked, i.e., before any GRANDPA signature is checked: [3](#0-2) 

Since a `Header`'s hash and `parent_hash` field are both fully attacker-chosen (headers are just SCALE-decoded structs, not verified against any real chain at this point), an attacker can craft a finite set of headers `H1..Hk` in `unknown_headers` such that `parent_hash(Hi) == hash(Hi+1 mod k)`, forming a closed cycle that never includes `base` or `from`. In `ancestry()`, `self.ancestry.get(&current_hash)` will then always return `Some` for members of this cycle, so `current_hash` never equals `base`, and the `while` loop never terminates — an unbounded/infinite loop, with `route` also growing without bound in memory.

This same unauthenticated verification path is also used by `verify_parachain_headers_with_grandpa_finality_proof` and by the fraud-proof path `verify_fraud_proof`, which independently calls `ancestry()` on both submitted proofs: [4](#0-3) 

### Impact Explanation
The trigger is reachable via `pallet_ismp::Call::handle_unsigned` with a `Message::Consensus` carrying a GRANDPA `ConsensusMessage::StandaloneChain`/`Relaychain`/`Polkadot` proof, which is an unsigned, feeless extrinsic: [5](#0-4) 

Critically, `ValidateUnsigned::validate_unsigned` for this pallet calls `Self::execute(messages.clone())` directly — meaning the vulnerable code path runs during **transaction-pool validation**, before the extrinsic is even included in a block: [6](#0-5) 

Any full node that receives the gossiped (unsigned) transaction executes this validation, so a single malicious message can hang block production/finalization and transaction-pool processing on every node that observes it — a chain-wide denial of service that halts ISMP message delivery entirely, matching the "route unable to deliver messages" acceptance criterion. No fees, signatures, or privileged roles are required to submit the payload.

### Likelihood Explanation
Likelihood is high: constructing a header cycle requires only picking arbitrary 32-byte `parent_hash` values across a handful of self-consistent fabricated `Header` structs — no cryptographic break, no relayer role, and no prior trusted state manipulation is needed, since the vulnerable `ancestry()` calls execute before the GRANDPA justification signature is checked.

### Recommendation
Bound `AncestryChain::ancestry` with a maximum iteration count (e.g., `unknown_headers.len() + 1`) and return an error (e.g., `Error::InvalidAncestry`/cycle-detected) if exceeded, or track visited hashes in a `BTreeSet` and abort on revisit. Apply the same bound identically in the fraud-proof path in `modules/ismp/clients/grandpa/src/consensus.rs`. Additionally, consider moving cheap structural bounds checks (e.g., `unknown_headers` length caps, uniqueness of header hashes) ahead of any graph traversal, mirroring the `MAX_PROOF_DEPTH` guard already used in `modules/consensus/pharos/primitives/src/spv.rs`.

### Proof of Concept
1. Craft headers `H1, H2, H3` (arbitrary `SubstrateHeader`s, e.g., differing by a dummy digest byte) such that `parent_hash(H1) = hash(H2)`, `parent_hash(H2) = hash(H3)`, `parent_hash(H3) = hash(H1)` — a 3-cycle with no connection to the trusted `consensus_state.latest_hash` or to any real chain hash.
2. Set `finality_proof.unknown_headers = [H1, H2, H3]` (or add more) with the highest-numbered header's hash set as `finality_proof.block`, and pair with any syntactically valid (but not necessarily cryptographically correct) `GrandpaJustification` blob targeting that same hash so SCALE decoding succeeds.
3. Submit `pallet_ismp::Call::handle_unsigned { messages: [Message::Consensus(ConsensusMessage { consensus_proof: encoded_proof, consensus_state_id: <victim GRANDPA client>, signer: vec![] })] }` as an unsigned transaction.
4. Every node's `validate_unsigned` calls `execute(messages)` → `GrandpaConsensusClient::verify_consensus` → `verify_grandpa_finality_proof` → `AncestryChain::ancestry(base.hash(), consensus_state.latest_hash)` (or `ancestry(from, target.hash())`), which enters the crafted 3-cycle and never returns, hanging the node's transaction-pool validation thread indefinitely.

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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L309-320)
```rust
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

**File:** modules/pallets/ismp/src/lib.rs (L358-382)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
		///
		/// Emits different message events based on the Message received if successful.
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
