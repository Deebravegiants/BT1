### Title
Unbounded GRANDPA justification (`precommits` / `votes_ancestries`) lets an unsigned `handle_unsigned` proof exhaust validator CPU for free - (File: modules/consensus/grandpa/primitives/src/justification.rs)

### Summary
`GrandpaJustification::verify_with_voter_set` iterates over the attacker-supplied `commit.precommits` and, for every precommit whose target differs from the base, calls `ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)` against the attacker-supplied `votes_ancestries` header list [1](#0-0) . Neither `Commit.precommits` nor `GrandpaJustification.votes_ancestries` is size-bounded before this loop runs, and this verification is reachable directly from the unsigned, feeless `Ismp::handle_unsigned` extrinsic, which pallet-ismp validates (and later executes) with no upfront fee or size gate [2](#0-1) . This mirrors the OpenCV CVE-2017-12600 class of bug: attacker-controlled input drives an amount of internal computation that is out of proportion to the cost paid by the attacker to submit it, causing CPU exhaustion on validating/executing nodes.

### Finding Description
`pallet-ismp`'s `handle_unsigned` call is explicitly an unsigned, free-of-charge extrinsic intended to let anyone submit ISMP messages "for free, provided they have valid proofs" [3](#0-2) . Before a submitted extrinsic ever reaches a block, `ValidateUnsigned::validate_unsigned` fully executes `Self::execute(messages.clone())` against every node's mempool, and the exact same `execute` call runs again at block-inclusion time in `handle_unsigned` itself [4](#0-3) . A consensus message routed to the GRANDPA client decodes into `GrandpaJustification<H>` and calls `justification.verify(...)`, which delegates to `verify_with_voter_set` [5](#0-4) .

Inside `verify_with_voter_set`:
- `finality_grandpa::validate_commit` already walks `commit.precommits`, but that is only the first pass.
- For each precommit, the code additionally calls `ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)` unless the target equals `base_hash` [1](#0-0) .
- `AncestryChain` is built directly from the submitter-controlled `votes_ancestries: Vec<H>` field of the justification [6](#0-5) , and there is no bound anywhere in this file (or in the pallet, or in the SCALE-decoding path) on the number of `precommits` or the number of `votes_ancestries` headers — a `grep` for `MAX_*PRECOMMIT`, `MAX_*HEADERS`, or `MAX_*ANCESTRY` constants in the repository returns no matches.
- `ancestry_chain.ancestry(...)` performs a graph walk backward through parent-hash links across the submitted header set; with `N` precommits and `M` ancestry headers, an attacker can force up to `O(N*M)` (or worse, depending on chain-shape) hash lookups and comparisons purely from the shapes of two `Vec` fields inside a SCALE-decoded, unsigned payload, with no economic cost.

Because the message is unsigned and free, and the whole verification (ed25519 signature checks per precommit plus the ancestry walk) runs twice per submission — once in mempool validation on every node, and once again during block execution — an attacker can flood the network with many such oversized justifications (or repeatedly resubmit variants, since the pool dedups only by content hash) to burn CPU across the whole validator/full-node set for a fraction of the cost a normal user pays, with no signed transaction fee to throttle the attack. This is analogous to the CVE-2017-12600 CPU-exhaustion DoS: unauthenticated/uncosted attacker input drives disproportionate internal computation.

Contrast this with the Pharos SPV path, which the codebase already hardened against exactly this class of issue via an explicit `MAX_PROOF_DEPTH` bound enforced before any node is walked [7](#0-6) , and a corresponding regression test proving that an over-deep proof is now rejected before its cost is paid [8](#0-7) . No equivalent bound exists for GRANDPA's `precommits`/`votes_ancestries`.

### Impact Explanation
This is a High-severity availability/DoS issue for the Hyperbridge relay chain and any parachain running `pallet-ismp` with the GRANDPA consensus client enabled. Because `handle_unsigned` is fee-less and unsigned, and validation happens on every node's mempool before inclusion, an attacker can:
- Force disproportionate CPU consumption on every full node/validator that receives the gossip transaction (mempool validation cost), and
- Force it again on the node(s) that include it in a block (execution cost),
with no signed-transaction fee to make repeated attempts costly. Sustained submission of maximally-sized justifications can degrade block production and transaction-pool responsiveness network-wide — a route being rendered unable to reliably process/deliver messages, which matches the "route unable to deliver messages" acceptance criterion for this program.

### Likelihood Explanation
Likelihood is high in principle: the entry point (`handle_unsigned`) is explicitly designed to be reachable by "anyone" with no signature or fee, and the vulnerable code path (`GrandpaJustification::verify_with_voter_set`) executes unconditionally as part of routing any GRANDPA `ConsensusMessage`, before any economically-costly gate. The only mitigating factors are: (a) SCALE-decoding itself imposes some practical ceiling on how large `precommits`/`votes_ancestries` can be within extrinsic/block size limits, and (b) `longevity: 25` limits how long a given submission lingers in the pool. Neither of these is a deliberate defense against this specific cost-amplification pattern, and both leave room for meaningfully-sized abusive payloads (many precommits crossed with many ancestry headers) well within normal extrinsic size limits.

### Recommendation
Impose an explicit upper bound on `GrandpaJustification.commit.precommits.len()` and `GrandpaJustification.votes_ancestries.len()` (sized to the actual GRANDPA authority-set size and expected ancestry depth) and reject the justification before any ed25519 verification or `AncestryChain::ancestry` walk is attempted — mirroring the `MAX_PROOF_DEPTH` pattern already used for the Pharos SPV verifier. Consider also capping the total number of `Message::Consensus` entries and their aggregate encoded size accepted per `handle_unsigned` batch at the `validate_unsigned` boundary, so that mempool-validation cost is proportional to a bounded, cheaply-checked quantity before any cryptographic or graph-walk work begins.

### Proof of Concept
Conceptual PoC (verification-time cost amplification, not a memory-safety bug):
1. Construct a `Message::Consensus(ConsensusMessage { consensus_proof, consensus_state_id: <GRANDPA state>, signer: vec![] })` where `consensus_proof` SCALE-encodes a `FinalityProof`/`GrandpaJustification` whose:
   - `commit.precommits` contains as many `SignedPrecommit` entries as fit within the extrinsic/block size limit, each targeting a distinct hash, and
   - `votes_ancestries` contains a maximal chain of headers such that `AncestryChain::ancestry(base_hash, target_hash)` must traverse many links for a large fraction of the precommits.
2. Submit this as an unsigned extrinsic via `Ismp::handle_unsigned([Message::Consensus(...)])`.
3. Observe that `ValidateUnsigned::validate_unsigned` (called by every peer's mempool) and later `Call::handle_unsigned`'s dispatch both invoke `Self::execute`, which reaches `verify_with_voter_set` and performs the full ed25519-signature-check loop plus the `ancestry` graph walk for every precommit not equal to the base hash, at no cost to the submitter since the extrinsic is both unsigned and rejected as invalid only *after* this work completes (or accepted if crafted to barely pass validate_commit but still burn maximal ancestry-walk time).
4. Repeat with many slightly-varied payloads (different trailing bytes/nonces) to bypass the pool's content-hash dedup and sustain the CPU load across the network.

I was unable to fully verify the internal implementation and asymptotic complexity of `AncestryChain::ancestry` in the `finality_grandpa` crate (external dependency, not indexed in this repo), so the precise growth rate (`O(N*M)` vs. worse) is an estimate based on the algorithm's use of an ancestor/parent-hash walk over the caller-supplied header set; the core finding — that `precommits` and `votes_ancestries` are unbounded on this attacker-reachable, feeless path — is confirmed directly from the code and repository-wide search for any such bound.

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

**File:** modules/pallets/ismp/src/lib.rs (L360-382)
```rust
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

**File:** modules/pallets/ismp/src/lib.rs (L605-626)
```rust
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T> {
		type Call = Call<T>;

		// empty pre-dispatch do we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L66-93)
```rust
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

**File:** modules/consensus/pharos/primitives/src/spv.rs (L82-87)
```rust
// Max legitimate proof length for a SHA-256 hexary trie: 64 nibbles of trie
// depth (one per hash byte nibble) plus the MSU root. Anything beyond this
// cannot correspond to a real trie path and is rejected to bound verifier
// work and prevent adversarial proofs from driving `nibble_at_depth` past
// the end of the 32-byte key hash.
pub const MAX_PROOF_DEPTH: usize = 65;
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
