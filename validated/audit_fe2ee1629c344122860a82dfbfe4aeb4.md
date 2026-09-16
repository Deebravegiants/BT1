### Title
Unbounded ancestry-walk in GRANDPA justification verification enables CPU-exhaustion DoS via `handle_unsigned` - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`GrandpaJustification::verify_with_voter_set` performs an ancestry walk for every precommit in a submitted justification, and the walk cost is proportional to attacker-supplied header-chain depth with no bound on the number of precommits or ancestry headers. Because this path is reached through `pallet-ismp`'s free, permissionless `handle_unsigned` extrinsic — and is *re-executed* by `validate_unsigned` on every node's mempool for every propagation/re-validation — a single malformed consensus message can trigger disproportionate CPU consumption across the network, mirroring the GitLab CVE-2022-2931 pattern of "malformed content causing high CPU usage."

### Finding Description
`AncestryChain::ancestry` walks parent-hash pointers one at a time until it hits the base hash: [1](#0-0) 

`verify_with_voter_set` invokes this walk once per precommit in `self.commit.precommits`, and the `GrandpaJustification` struct places no upper bound on either `commit.precommits` or `votes_ancestries`: [2](#0-1) [3](#0-2) 

The only bound on the size of the submitted headers/precommits is the runtime's general extrinsic-length/weight limit, not a domain-specific cap tied to actual relay-chain finality semantics (real GRANDPA rounds have one precommit per validator and a short ancestry route; nothing here enforces that shape before doing the work). An attacker can therefore submit a `votes_ancestries` vector padded with many headers that form long forking chains, together with several precommits that each force a full ancestry walk, driving up total verification cost (`O(precommits × ancestry_depth)`).

This verifier is reached from the GRANDPA `ConsensusClient::verify_consensus`, which handles `ConsensusMessage::StandaloneChain`/`Relaychain`/`Polkadot` variants and calls `verify_grandpa_finality_proof` / `verify_parachain_headers_with_grandpa_finality_proof` directly on attacker-supplied `FinalityProof`/`ParachainHeadersWithFinalityProof` data: [4](#0-3) [5](#0-4) 

The entry point into this code is `pallet_ismp::Call::handle_unsigned`, an unsigned, feeless, permissionless extrinsic that dispatches `Message::Consensus` to the appropriate consensus client: [6](#0-5) 

Critically, `ValidateUnsigned::validate_unsigned` for `pallet-ismp` re-runs the *entire* `Self::execute(messages.clone())` — including full GRANDPA verification — every time the transaction pool validates or re-validates the extrinsic (on submission, on every peer gossip re-check, and on block-building attempts), multiplying the cost across every full node on the network rather than a single execution: [7](#0-6) 

### Impact Explanation
Because `handle_unsigned` messages are validated for free by every relay/full node's transaction pool before being gossiped, and validation re-executes the costly ancestry walks each time, a single crafted `ConsensusMessage` can cause outsized CPU consumption cluster-wide — a network-level denial-of-service against the message-dispatch path used by relayers to deliver consensus updates and ISMP messages. This can degrade or halt honest consensus-update and request/response processing, a route-unable-to-deliver-messages condition for the affected chain.

### Likelihood Explanation
The `handle_unsigned` call is explicitly designed to be free and callable by anyone with a well-formed message and syntactically valid proof structure (no correctness of the finality proof is required to *begin* the expensive walk — decoding succeeds and the walk executes before final signature/threshold checks reject it). Building an oversized `votes_ancestries`/`precommits` payload requires no privileged access, no real validator keys, and no economic cost beyond extrinsic size limits, making this readily reachable by any unprivileged relayer/attacker.

### Recommendation
Enforce explicit, protocol-appropriate bounds before performing any ancestry walk: cap `votes_ancestries.len()` and `commit.precommits.len()` to values consistent with the real authority-set size, and reject the justification early if either bound is exceeded. Consider walking with a bounded step counter and aborting with an error once a maximum ancestry depth is exceeded, so an attacker cannot force unbounded parent-hash traversal work.

### Proof of Concept
Not independently reproduced; this analysis is based on static code review of the reachable data flow (`handle_unsigned` → `GrandpaConsensusClient::verify_consensus` → `verify_grandpa_finality_proof`/`verify_parachain_headers_with_grandpa_finality_proof` → `GrandpaJustification::verify_with_voter_set` → `AncestryChain::ancestry`) and the absence of any length/depth cap on `votes_ancestries`/`precommits` prior to the walk. Confirming actual exploitability (i.e., whether extrinsic-length/weight limits in the deployed runtimes already make this impractical) would require constructing a concrete oversized `GrandpaJustification` payload and benchmarking `validate_unsigned` CPU time, which is unverified here.

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L109-134)
```rust
		let mut visited_hashes = BTreeSet::new();
		for signed in self.commit.precommits.iter() {
			let message = finality_grandpa::Message::Precommit(signed.precommit.clone());

			check_message_signature::<_, _>(
				&message,
				&signed.id,
				&signed.signature,
				self.round,
				set_id,
			)?;

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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L169-173)
```rust
			ConsensusMessage::StandaloneChain(standalone_chain_message) => {
				let (consensus_state, header, _, _) = verify_grandpa_finality_proof(
					consensus_state,
					standalone_chain_message.finality_proof,
				)?;
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
