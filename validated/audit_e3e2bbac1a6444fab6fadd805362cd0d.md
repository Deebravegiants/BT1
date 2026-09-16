### Title
GRANDPA finality-proof ancestry walk loops forever on unauthenticated, self-referential header cycles — CPU exhaustion before signature verification - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`AncestryChain::ancestry` walks a parent-hash linked list built entirely from attacker-supplied `unknown_headers`/`votes_ancestries` before any cryptographic signature is checked. A submitter can craft a header whose `parent_hash` equals its own hash (or a short cycle of two headers), causing the `while current_hash != base` loop to spin forever. This is reachable from the permissionless, unsigned `pallet_ismp::handle_unsigned` extrinsic, so every node performing mempool validation of the transaction pins a CPU core indefinitely — the same bug class as GHSA‑p86g‑xrr2‑pf7c (CoreWCF's pre‑authentication infinite-loop framing handshake CPU exhaustion).

### Finding Description
`AncestryChain::ancestry` is: [1](#0-0) 

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

`self.ancestry` is a `BTreeMap<Hash, Header>` built directly from attacker-submitted headers with no validation that they form an acyclic chain: [2](#0-1) 

The critical defect is *where* this walk is invoked in `verify_grandpa_finality_proof`: [3](#0-2) 

```rust
let headers = AncestryChain::<H>::new(&finality_proof.unknown_headers);
let target = finality_proof.unknown_headers.iter().max_by_key(|h| *h.number())...;
if target.hash() != finality_proof.block { Err(Error::LatestBlockMismatch)? }
let justification = GrandpaJustification::<H>::decode_all(&mut &finality_proof.justification[..])...;
if justification.commit.target_hash != finality_proof.block { Err(...)? }
let from = consensus_state.latest_hash;
let base = finality_proof.unknown_headers.iter().min_by_key(|h| *h.number())...;
if base.number() < &consensus_state.latest_height {
    headers.ancestry(base.hash(), consensus_state.latest_hash)...;
}
let finalized = headers.ancestry(from, target.hash())...;   // <-- runs BEFORE justification.verify()
justification.verify(consensus_state.current_set_id, &consensus_state.current_authorities)...;
```

`unknown_headers` is entirely attacker-controlled (arbitrary `Header` structs, no signature attached to individual headers). `target`/`base` are derived purely from the max/min block number in this attacker list, and `finality_proof.block` / `justification.commit.target_hash` can trivially be set to match `target.hash()` by the attacker (these are just equality assertions on attacker-chosen values, not signature checks). The only real cryptographic check, `justification.verify(...)`, happens *after* the `headers.ancestry(from, target.hash())` call on line 88.

An attacker can therefore submit a single header `X` with `X.parent_hash == X.hash()` (a self-loop) or a two-header cycle `A.parent_hash == hash(B)`, `B.parent_hash == hash(A)`, choose `X.number()` (or both headers' numbers) high enough to skip the first `ancestry()` guard branch, and set `finality_proof.block = X.hash()` and a minimally-decodable `justification` whose `commit.target_hash = X.hash()`. Because `from = consensus_state.latest_hash` (the node's trusted, real hash) is never equal to `X.hash()`, the `while current_hash != base` loop toggles between `X` (or `A`/`B`) forever, since every lookup in the map succeeds and the exit condition can never be reached.

This is reachable through `pallet_ismp::handle_unsigned`, an intentionally free, unsigned, unauthenticated extrinsic: [4](#0-3) 

and, critically, through `ValidateUnsigned::validate_unsigned`, which runs `Self::execute(messages.clone())` (and therefore the full consensus-message verification path, including the vulnerable ancestry walk) during **transaction-pool validation**, before the extrinsic is even included in a block: [5](#0-4) 

The GRANDPA client's `verify_consensus` decodes the untrusted `ConsensusMessage` and dispatches straight into `verify_grandpa_finality_proof`: [6](#0-5) 

### Impact Explanation
Because the hang occurs inside `validate_unsigned` (mempool/tx-pool validation), every full node that receives the malicious unsigned extrinsic — before it is even confirmed on-chain — will spin one thread at 100% CPU indefinitely trying to complete the ancestry walk. A handful of such crafted extrinsics broadcast to the network can pin multiple worker threads across all validating/relaying nodes, exactly mirroring the CoreWCF advisory's "pin one server thread-pool worker at 100% CPU per connection... with a few connections, CPU usage can be exhausted." Because `pallet-ismp`'s unsigned messages are specifically designed to allow *anyone* to submit ISMP consensus/request messages for free, this is trivially reachable without any relayer key, staked collator, or governance permission — a genuine unauthenticated High-severity DoS that can stall consensus-client updates and therefore block delivery of all cross-chain messages routed through GRANDPA-secured chains (a state machine "route unable to deliver messages").

### Likelihood Explanation
High. The attacker needs no privileged role, no valid GRANDPA authority signature, and no economic stake — only the ability to submit a free unsigned extrinsic (which is explicitly supported by the pallet's design) with a self-referential or 2-cycle header list. Crafting such headers is trivial (arbitrary `Header` fields, computed hash, and a matching `parent_hash`); no cryptography needs to be broken.

### Recommendation
Reorder `verify_grandpa_finality_proof` so `justification.verify(...)` (or at minimum, an acyclicity/bounded-depth check on `unknown_headers`) runs strictly before any `AncestryChain::ancestry` walk is performed. Additionally, harden `AncestryChain::ancestry` itself to be defensive regardless of call order: bound the number of iterations by `self.ancestry.len() + 1` (a valid ancestry route can never revisit a hash) and return `Error::NotDescendent` once that bound is exceeded, or track `visited` hashes and abort on a repeat.

### Proof of Concept
1. Construct header `X` (arbitrary body) such that `X.parent_hash = BlakeTwo256::hash_of(&X)` (self-referential parent) — feasible by iterating a nonce/extra field until the hash matches, or more simply using two headers `A`,`B` with `A.parent_hash = hash(B)` and `B.parent_hash = hash(A)`.
2. Set `unknown_headers = [X]` (or `[A, B]`), pick `X.number()` (or `min(A.number(),B.number())`) `>= consensus_state.latest_height` so the first `ancestry()` guard branch in `verify_grandpa_finality_proof` is skipped.
3. Set `finality_proof.block = X.hash()`.
4. Build a `GrandpaJustification` that SCALE-decodes successfully with `commit.target_hash = X.hash()` (precommits can be an empty/garbage vector — decoding does not validate signatures at this stage).
5. Wrap this into `ConsensusMessage::<Relay variant with GRANDPA> -> Message::Consensus(ConsensusMessage { consensus_proof, consensus_state_id, signer: vec![] })` and submit via `pallet_ismp::Call::handle_unsigned { messages: vec![msg] }` as an unsigned transaction.
6. Any node performing `ValidateUnsigned::validate_unsigned` for this extrinsic calls `Self::execute(messages)` → GRANDPA `verify_consensus` → `verify_grandpa_finality_proof` → `headers.ancestry(from, target.hash())`, which loops forever between `X` (or `A`/`B`), consuming 100% CPU on that thread with no timeout.

(Note: I was not able to execute this PoC in a live environment; the analysis is based on static review of the exact call ordering in `modules/consensus/grandpa/verifier/src/lib.rs` and `modules/consensus/grandpa/primitives/src/justification.rs`. The precise SCALE layout needed for a minimally-valid `GrandpaJustification`/`ConsensusMessage` envelope should be confirmed against `modules/ismp/clients/grandpa/src/messages.rs`, which I did not have time to fully inspect in this session.)

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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L69-106)
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

		let mut intermediates = BTreeMap::new();

		// match over the message
		match consensus_message {
			ConsensusMessage::Polkadot(relay_chain_message) => {
				let headers_with_finality_proof = ParachainHeadersWithFinalityProof {
					finality_proof: relay_chain_message.finality_proof,
					parachain_headers: relay_chain_message.parachain_headers,
				};

				let (consensus_state, parachain_headers) =
					verify_parachain_headers_with_grandpa_finality_proof(
						consensus_state,
						headers_with_finality_proof,
					)?;
```
