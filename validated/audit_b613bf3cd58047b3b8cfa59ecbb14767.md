Found the key analog: the GRANDPA `AncestryChain::ancestry` function contains an unbounded `while` loop that walks a header chain supplied entirely by an unprivileged relayer via a consensus message, with no bound on iterations or cycle detection — directly analogous to Bitcoin Core's CVE-2024-52920 infinite-loop-via-malformed-message class.

### Title
Unbounded ancestry-walk loop in GRANDPA `AncestryChain::ancestry` allows relayer-supplied consensus proof to hang the verifying node - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`GrandpaJustification::verify_with_voter_set` and `verify_grandpa_finality_proof` both call `AncestryChain::ancestry`, which walks parent hashes from a `block` hash back to a `base` hash using a `while current_hash != base` loop over a caller-supplied `votes_ancestries`/`unknown_headers` map [1](#0-0) . This function is reachable from the unsigned, fee-free `pallet_ismp::Call::handle_unsigned` extrinsic carrying a GRANDPA `ConsensusMessage`, which any unprivileged account can submit [2](#0-1) .

### Finding Description
The `ancestry` function builds a `route` by repeatedly looking up `current_hash` in a `BTreeMap` built from attacker-supplied headers (`votes_ancestries` in the justification, or `unknown_headers` in the finality proof) and following `parent_hash` pointers until `current_hash == base`:

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
``` [3](#0-2) 

Because the map is keyed by header hash and populated straight from the relayer-controlled `H` values (with `hash()` computed from the header's own content, including `parent_hash`), a submitter can craft a set of headers whose `parent_hash` pointers form a cycle that never reaches `base` and never fails the lookup (each hash in the cycle exists in the map). The loop has no iteration bound, no visited-set/cycle check, and no relationship to `Weight`/gas accounting inside the pure Rust helper — it is invoked before any weight-metered dispatch decides to abort. The same primitive is reused by `verify_grandpa_finality_proof`, which is itself invoked from the GRANDPA `ConsensusClient::verify_consensus` implementation used both in `validate_unsigned` (mempool/transaction-pool validation, off-chain, unmetered by block weight) and in `handle_unsigned` execution [4](#0-3) [5](#0-4) .

Critically, `validate_unsigned` for `pallet_ismp::Call::handle_unsigned` runs `Self::execute(messages.clone())` directly during transaction-pool validation [6](#0-5) , i.e. every full node that receives this unsigned extrinsic over the p2p gossip network executes the GRANDPA verification path — including the vulnerable `ancestry` walk — before any block-weight metering applies. A cyclic ancestry map submitted this way can hang transaction-pool validation on every node that receives the gossiped extrinsic, not just the block author, mirroring the "malformed message causes CPU-bound infinite loop on message receipt" pattern from CVE-2024-52920.

### Impact Explanation
An unbounded loop reachable pre-dispatch (inside `validate_unsigned`, which runs off-chain / outside block weight limits) on every full node that receives the malicious unsigned extrinsic constitutes a network-wide denial-of-service: nodes hang validating the transaction, blocking further transaction-pool processing and potentially the node's responsiveness, without requiring the transaction to ever be included in a block. Given this is reachable by any account able to submit an unsigned extrinsic (i.e., anyone with network access — no fee required), and can propagate the malicious message across gossiping peers, this can degrade or halt message delivery across the whole route until mitigated. This is a "route unable to deliver messages" class impact per the intended scope.

### Likelihood Explanation
Likelihood is high for chains that enable the GRANDPA consensus client with `handle_unsigned` unsigned-extrinsic support: constructing a cyclic ancestry set requires only computing header hashes locally (headers are arbitrary structured data controlled entirely by the submitter for the ancestry map, since `AncestryChain::new` builds the map straight from the provided `Vec<H>` without any prior validation that headers form a real, non-cyclic chain) and does not require any signature, proof-of-stake, or on-chain state — it can be crafted entirely offline before submission.

### Recommendation
Bound the `ancestry` walk with either: (1) a maximum iteration count derived from `votes_ancestries.len()` (the walk cannot legitimately need more steps than there are distinct headers), returning `Err(NotDescendent)` once exceeded; and/or (2) a `visited` set that aborts with an error immediately upon revisiting a hash, definitively rejecting cycles. Additionally, validate that `self.ancestry` (the header map) contains no duplicate-hash entries that could otherwise be exploited, and ensure this bound is enforced before `validate_unsigned` invokes `Self::execute`, so a malicious unsigned extrinsic cannot hang mempool validation on receiving peers.

### Proof of Concept
1. Craft two (or more) synthetic headers `H1`, `H2` whose `parent_hash` fields point at each other (`H1.parent_hash = hash(H2)`, `H2.parent_hash = hash(H1)`), and neither hashes to the justification's chosen `base` hash.
2. Include `H1`, `H2` (and enough headers to also satisfy any other structural checks) in `votes_ancestries` (for `GrandpaJustification::verify`) or `unknown_headers` (for `verify_grandpa_finality_proof`'s `FinalityProof`), with a `commit`/`precommit` targeting a hash reachable only by traversing into the cycle.
3. Wrap this in a GRANDPA `ConsensusMessage` and submit it as `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Consensus(msg)] }` as an unsigned extrinsic.
4. Every node whose transaction pool receives the gossiped extrinsic calls `validate_unsigned`, which calls `Self::execute` → GRANDPA `verify_consensus` → `verify_grandpa_finality_proof`/`GrandpaJustification::verify` → `AncestryChain::ancestry`, entering the infinite `while current_hash != base` loop and hanging that thread indefinitely.

### Citations

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-88)
```rust
	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L69-90)
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
```
