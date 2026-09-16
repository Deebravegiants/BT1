### Title
Unbounded GRANDPA Justification Precommits/Ancestry Allow Free Resource-Exhaustion via `handle_unsigned` - (File: modules/consensus/grandpa/primitives/src/justification.rs)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic is free and unsigned, and it routes GRANDPA `ConsensusMessage`s to `GrandpaConsensusClient::verify_consensus`, which decodes and verifies a `GrandpaJustification` whose `commit.precommits` and `votes_ancestries` vectors have no size bound. Every node that receives this transaction in gossip must run full signature verification and ancestry-chain reconstruction over these attacker-controlled, unbounded collections before rejecting an invalid proof — mirroring the GitLab CVE-2023-0121 pattern of unmetered resource consumption driven by an attacker-supplied artifact.

### Finding Description
`GrandpaJustification::verify_with_voter_set` iterates over `self.commit.precommits` and, for each entry, performs an Ed25519-family signature check (`check_message_signature`) and an ancestry walk (`ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)`) that itself scans the `votes_ancestries` map: [1](#0-0) 

Both `commit.precommits` and `votes_ancestries` are plain `Vec<H>`/`Vec<SignedPrecommit>` fields with no `MaxEncodedLen`/bound, populated straight from `Decode`: [2](#0-1) 

This message reaches every full node for free: `pallet_ismp::Call::handle_unsigned` is validated by `ValidateUnsigned::validate_unsigned`, which unconditionally calls `Self::execute(messages.clone())` — i.e., full consensus-proof verification — during transaction-pool validation, before any fee is charged or block inclusion occurs: [3](#0-2) 

The consensus message envelope (`RelayChainMessage`/`StandaloneChainMessage`) and its nested `FinalityProof`/`ParachainHeaderProofs` maps are likewise unbounded `Vec`/`BTreeMap` collections decoded directly from the submitter's bytes: [4](#0-3) 

An attacker can craft (or replay structurally, without needing a valid signature — verification runs on all precommits before determining the proof is invalid) a `GrandpaJustification` whose `precommits` and `votes_ancestries` are padded up to the block/extrinsic length limit, forcing every node validating the unsigned transaction in its mempool (and every node re-validating it on gossip propagation and re-broadcast) to perform O(n) signature checks plus O(n·m) ancestry-chain traversals, all for free, repeatedly, with no economic cost to the attacker (`handle_unsigned` explicitly waives fees). Contrast this with the request/response handlers, which already dedupe and cap batch content early (`dedup_requests`, per-key checks) before expensive proof verification runs, showing that other paths already recognize the need to bound work — the GRANDPA justification path does not.

### Impact Explanation
This is a direct denial-of-service vector against Hyperbridge/parachain nodes that support the GRANDPA consensus client: since `handle_unsigned` messages are free and validated by every node in the network on every gossip hop, an attacker can repeatedly submit maximally-padded, invalid justifications to force expensive signature verification and ancestry traversal work on all validating nodes without paying any transaction fee, degrading network-wide throughput and node responsiveness — the same "high resource consumption" bug class as CVE-2023-0121. Because verification happens before consensus state is updated, this does not directly forge state, but a sustained attack can stall relayer message delivery and validator resource availability for the affected chain.

### Likelihood Explanation
Any unprivileged actor can construct and broadcast such a message since `handle_unsigned` requires no signature or fee, and `ConsensusMessage`/`FinalityProof`/`GrandpaJustification` are decoded and processed with no length caps prior to the expensive cryptographic/ancestry work. The only natural bound is the substrate block/extrinsic-length limit, which for a moderately sized chain still permits tens of thousands of bogus precommits/ancestry headers per submission, and submissions can be repeated indefinitely at no cost.

### Recommendation
Bound `commit.precommits` and `votes_ancestries` (and the outer `ConsensusMessage`/`ParachainHeaderProofs` collections) to a sane maximum before any signature check or ancestry walk is attempted, mirroring the pattern used elsewhere in the codebase (e.g., `MAX_PROOF_DEPTH` in `modules/consensus/pharos/primitives/src/spv.rs`, `MAX_VALIDATORS` in the Pharos state-proof verifier, and the early `dedup_requests`/size checks in the ISMP request/response handlers). Reject a justification outright if these counts exceed the bound, before invoking `finality_grandpa::validate_commit` or performing any per-precommit signature verification.

### Proof of Concept
1. Submit a `pallet_ismp::Call::handle_unsigned` extrinsic carrying `Message::Consensus(ConsensusMessage { consensus_state_id: <GRANDPA client>, consensus_proof: <encoded ConsensusMessage::Polkadot(RelayChainMessage{ finality_proof, parachain_headers }) >, signer: vec![] })`.
2. Craft `finality_proof.justification` as a SCALE-encoded `GrandpaJustification` whose `commit.precommits` contains as many `SignedPrecommit` entries (with arbitrary/garbage signatures) as fit under the extrinsic length limit, and whose `votes_ancestries` similarly contains the maximum number of dummy headers.
3. Broadcast repeatedly; every validating node runs `check_message_signature` and `ancestry_chain.ancestry(...)` over the full unbounded set inside `validate_unsigned`/`execute` for each submission, for free, before the proof is ultimately rejected as invalid.

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

**File:** modules/ismp/clients/grandpa/src/messages.rs (L26-48)
```rust
#[derive(Clone, Debug, Encode, Decode)]
pub enum ConsensusMessage {
	/// This is the variant representing the standalone chain
	StandaloneChain(StandaloneChainMessage),
	/// This is the variant representing the Polkadot relay chain
	Polkadot(RelayChainMessage),
	/// This is the variant representing a standalone relaychain
	Relaychain(RelayChainMessage),
}

#[derive(Clone, Debug, Encode, Decode)]
pub struct StandaloneChainMessage {
	/// finality proof
	pub finality_proof: FinalityProof<SubstrateHeader>,
}

#[derive(Clone, Debug, Encode, Decode)]
pub struct RelayChainMessage {
	/// finality proof
	pub finality_proof: FinalityProof<SubstrateHeader>,
	/// parachain headers
	pub parachain_headers: BTreeMap<H256, ParachainHeaderProofs>,
}
```
