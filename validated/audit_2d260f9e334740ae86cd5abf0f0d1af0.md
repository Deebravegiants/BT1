I found a strong analog in `GrandpaJustification::verify` — the same CWE-834 (excessive iteration driven by an untrusted "size") bug class as the pypdf report, reachable by an unprivileged relayer submitting an unsigned `handle_unsigned` extrinsic.

### Title
Unbounded GRANDPA precommit/ancestry iteration lets an unprivileged relayer force long runtimes on every full node's mempool - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
### Finding Description
`GrandpaJustification::verify_with_voter_set` iterates over `self.commit.precommits` and, for every precommit, walks the block-by-block `ancestry` chain from the precommit's target hash back to the computed `base_hash` [1](#0-0) . Both `self.commit.precommits` and `self.votes_ancestries` are attacker-controlled fields decoded directly from the untrusted `ConsensusMessage` proof bytes submitted as part of a `pallet_ismp::Call::handle_unsigned` extrinsic — there is no upper bound on the number of precommits, nor on the length of the ancestry chain (`AncestryChain::ancestry` walks `current_hash = current_header.parent_hash()` in a `while` loop bounded only by the size of the attacker-supplied `votes_ancestries` map) [2](#0-1) . This mirrors the pypdf issue exactly: an untrusted "count"/"size"-like value (here, the number of precommits × ancestry chain depth) is trusted to drive nested loop bounds before any validation gate gets a chance to reject the input cheaply.

This entry point is reachable pre-dispatch: `pallet_ismp`'s `validate_unsigned` calls `Self::execute(messages.clone())`, which calls `handle_incoming_message`, which for a `Message::Consensus` invokes `GrandpaConsensusClient::verify_consensus` → `verify_grandpa_finality_proof` → `justification.verify(...)` [3](#0-2) [4](#0-3) [5](#0-4) . Because `pallet_ismp` uses unsigned transactions specifically so cross-chain messages can be submitted "for free" [6](#0-5) , this verification (including the unbounded precommit/ancestry walk) runs during transaction-pool validation on every full node that receives the gossiped extrinsic, before any weight charge or fee is assessed.

### Impact Explanation
An unprivileged party can submit a single unsigned extrinsic carrying a `ConsensusMessage` with a large number of forged/garbage precommits (each requiring an `ed25519_verify` and, unless the target equals the base, a full ancestry walk through a large attacker-supplied `votes_ancestries` vector) [1](#0-0) . Because the check runs in `validate_unsigned` — the mempool gate, prior to weight metering — this can degrade transaction-pool validation performance across the network's relaying full nodes for the effort of crafting one oversized proof blob, i.e. a route to unable-to-deliver-messages / network-availability degradation rather than fund loss, but squarely the "long runtimes / DoS via unvalidated size-like field" class described in the report.

### Likelihood Explanation
The extrinsic is unsigned and free by design (no fee, no signature required) [6](#0-5) , so any network participant can submit it repeatedly at negligible cost. The codebase's own commentary shows the authors are actively hardening exactly this class of attacker-controlled-size DoS elsewhere (`MAX_PROOF_DEPTH` in the Pharos SPV code, `subtree_heights`'s `max_subtrees` cap, the zstd-bomb `encoded_call_size` gate in `pallet-call-decompressor`) [7](#0-6) [8](#0-7) [9](#0-8) , but no equivalent bound exists on `commit.precommits.len()` or `votes_ancestries.len()` in the GRANDPA justification path.

### Recommendation
Add explicit upper bounds — analogous to `MAX_PROOF_DEPTH`/`max_subtrees` used elsewhere in this codebase — on `GrandpaJustification::commit.precommits.len()` and `votes_ancestries.len()` (and/or the resulting ancestry chain length walked per precommit) at decode time or at the top of `verify_with_voter_set`, rejecting oversized justifications before any signature or ancestry-walk work is performed, mirroring the `encoded_call_size` early-reject pattern in `pallet-call-decompressor::decompress`.

### Proof of Concept
1. Craft a `ConsensusMessage::Polkadot`/`Relaychain`/`StandaloneChain` variant wrapping a `GrandpaJustification` whose `commit.precommits` contains a very large number of entries (each with a syntactically valid but unrelated `target_hash`), and whose `votes_ancestries` contains a long, deliberately deep synthetic header chain.
2. Wrap it in a `Message::Consensus(ConsensusMessage { consensus_proof, consensus_state_id, signer: vec![] })` and submit it via `pallet_ismp::Call::handle_unsigned { messages: vec![msg] }` as an unsigned transaction, exactly as in the existing test harness pattern [10](#0-9) .
3. Every full node that receives the gossiped extrinsic runs `validate_unsigned` → `execute` → `verify_grandpa_finality_proof` → `justification.verify(...)`, performing O(precommits × ancestry-depth) work and signature checks before the transaction is ever rejected for being invalid, at zero cost to the submitter.

### Citations

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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L69-96)
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

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L1098-1119)
```rust
	#[test]
	fn test_over_deep_proof_rejected() {
		// Regression: prior to the MAX_PROOF_DEPTH guard, a proof with more
		// than 65 nodes would drive `nibble_at_depth` past the 32-byte key
		// hash and panic with index-out-of-bounds inside on-chain execution.
		// Now it must return `ProofTooDeep` cleanly.
		let dummy_leaf = make_leaf(b"k", b"v");
		let mut proof: Vec<PharosProofNode> = Vec::with_capacity(MAX_PROOF_DEPTH + 1);
		for _ in 0..MAX_PROOF_DEPTH {
			proof.push(node(vec![0u8; INTERNAL_NODE_LEN], 0, 0));
		}
		proof.push(node(dummy_leaf, 0, 0));
		assert_eq!(proof.len(), MAX_PROOF_DEPTH + 1);

		let root = [0u8; 32];
		assert!(matches!(verify_proof(&proof, b"k", b"v", &root), Err(Error::ProofTooDeep)));
		assert!(matches!(verify_membership_proof(&proof, b"k", &root), Err(Error::ProofTooDeep)));
		assert!(matches!(
			verify_non_existence_proof(&proof, b"k", &root, &[]),
			Err(Error::ProofTooDeep)
		));
	}
```

**File:** modules/consensus/beefy/prover/src/relay.rs (L213-229)
```rust
fn subtree_heights(leaves_length: u64) -> Vec<u64> {
	let max_subtrees = 1024;
	let mut indices = vec![];
	let mut i = 0;
	let mut current = leaves_length;

	while i < max_subtrees {
		if current == 0 {
			break;
		}

		let log = current.ilog2();
		indices.push(log as u64);
		current = current - u64::pow(2, log);

		i += 1;
	}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L220-253)
```rust
	pub fn decompress(
		compressed_bytes: Vec<u8>,
		encoded_call_size: u32,
	) -> Result<Vec<u8>, DispatchError> {
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);

		let mut decoder = StreamingDecoder::new(compressed_bytes.as_slice())
			.map_err(|_| Error::<T>::DecompressionFailed)?;

		let claimed = encoded_call_size as usize;
		let mut result = Vec::new();
		let mut chunk = vec![0u8; 4096];

		loop {
			let n = decoder.read(&mut chunk).map_err(|_| Error::<T>::DecompressionFailed)?;
			if n == 0 {
				break;
			}
			if result.len() + n > claimed {
				return Err(Error::<T>::DecompressionFailed.into());
			}
			result.extend_from_slice(&chunk[..n]);
		}

		ensure!(result.len() == claimed, Error::<T>::DecompressionFailed);

		Ok(result)
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L558-589)
```rust
#[test]
fn consensus_messages_without_state_update_get_unique_provides_tags() {
	use ismp::messaging::ConsensusMessage;
	use polkadot_sdk::{
		frame_support::pallet_prelude::ValidateUnsigned,
		sp_runtime::transaction_validity::TransactionSource,
	};

	new_test_ext().execute_with(|| {
		let host = Ismp::default();
		setup_mock_client::<_, Test>(&host);

		// Builds a consensus message whose proof carries the sentinel prefix so the
		// mock consensus client returns no commitments (no StateMachineUpdated).
		let make = |suffix: &[u8]| {
			let mut consensus_proof = b"__no_state_update__".to_vec();
			consensus_proof.extend_from_slice(suffix);
			Message::Consensus(ConsensusMessage {
				consensus_proof,
				consensus_state_id: MOCK_CONSENSUS_STATE_ID,
				signer: vec![],
			})
		};

		let validate = |msg: Message| {
			let call = pallet_ismp::Call::<Test>::handle_unsigned { messages: vec![msg] };
			<pallet_ismp::Pallet<Test> as ValidateUnsigned>::validate_unsigned(
				TransactionSource::External,
				&call,
			)
			.expect("consensus message should be a valid unsigned transaction")
		};
```
