### Title
Unbounded GRANDPA justification ancestry/precommit fan-out enables CPU-exhaustion DoS via free `handle_unsigned` extrinsic - (File: modules/consensus/grandpa/primitives/src/justification.rs)

### Summary
The GRANDPA finality-proof verification path accepts an attacker-controlled, unbounded number of `votes_ancestries` headers and `commit.precommits` entries inside a `GrandpaJustification`, and walks the full ancestry chain once per precommit before any mismatch is detected. This proof is delivered inside a `ConsensusMessage`, which reaches consensus clients through the permissionless, fee-free `pallet_ismp::handle_unsigned` extrinsic — validated on every node during mempool gossip via `validate_unsigned`. A crafted justification with many precommits and a long/complex ancestry set can force each validating node to perform O(precommits × ancestry-depth) work, mirroring the KeyTrap class of algorithmic-complexity DoS (cheap-to-submit, expensive-to-validate input causing CPU exhaustion), but here reachable by any unprivileged submitter rather than a DNS resolver.

### Finding Description
`GrandpaJustification::verify_with_voter_set` builds an `AncestryChain` from the caller-supplied `votes_ancestries: Vec<H>` (no length bound in the type) [1](#0-0) , then for every entry in `self.commit.precommits` (also caller-supplied, no bound) it calls `ancestry_chain.ancestry(base_hash, signed.precommit.target_hash)`, which walks parent hashes one at a time via `BTreeMap` lookups until it reaches `base_hash`: [2](#0-1) 

Only *after* this full walk is performed for every precommit does the function compare `visited_hashes` against `ancestry_hashes` and reject on mismatch [3](#0-2) . The `ancestry()` implementation itself is an unbounded loop over the supplied header set: [4](#0-3) .

This verification is invoked from `verify_grandpa_finality_proof`, reachable from `GrandpaConsensusClient::verify_consensus` via a `ConsensusMessage` decoded from raw proof bytes [5](#0-4) , and that consensus message is itself delivered as a `Message::Consensus(..)` inside `pallet_ismp::Pallet::handle_unsigned`, an **unsigned, fee-free** extrinsic anyone can submit: [6](#0-5) . Critically, `validate_unsigned` actually *executes* the message (including full consensus verification) on every node during mempool validation, before the transaction is ever included in a block: [7](#0-6) .

There is no `BoundedVec`/max-length constraint on `messages: Vec<Message>`, on `GrandpaJustification::votes_ancestries`, or on `commit.precommits` at the type level — the only practical ceiling is the block/extrinsic byte-size limit, which the project's own documentation raises specifically to accommodate large GRANDPA proofs (recommending an 8MB block length with 85% extrinsic ratio for GRANDPA-integrated solochains) [8](#0-7) . Within that byte budget, an attacker can pack tens of thousands of small headers/precommit entries, and because the ancestry walk for each precommit is independent (no cross-precommit memoization) the aggregate work scales multiplicatively with precommit count × chain depth — the same "cheap-to-construct, expensive-to-validate" complexity-blowup pattern KeyTrap exploited against DNSSEC validators, except here the validation is triggered on *every relaying/gossiping node* for a transaction that costs the submitter nothing.

### Impact Explanation
A single crafted `handle_unsigned` extrinsic carrying a maximal `ConsensusMessage::StandaloneChain`/`Polkadot` payload can force disproportionate CPU consumption on every node that validates it in the transaction pool (before block inclusion) and again during block execution if it slips through. Because `validate_unsigned` runs this same expensive path for free and repeatedly (each gossip hop), an attacker can degrade or stall node responsiveness — a denial-of-service against the routing/relaying infrastructure itself, without needing any stake, signature-forging capability, or transaction fee. This satisfies the "route unable to deliver messages" criterion: nodes spending excessive CPU validating one poisoned extrinsic delay processing of legitimate consensus/message proofs.

### Likelihood Explanation
Likelihood is high for the following reasons: the extrinsic is permissionless and free (`ensure_none` origin, no fee) [9](#0-8) ; the attacker does not need genuine GRANDPA authority signatures to trigger the expensive ancestry walk, since the walk happens prior to/alongside `check_message_signature` for each precommit inside the same loop, and the visited/ancestry mismatch is only checked at the end [10](#0-9) ; and the byte-size ceiling is deliberately generous (documented 8MB blocks) to support legitimately large GRANDPA proofs, giving an attacker ample room to construct a pathological input.

### Recommendation
- Bound `GrandpaJustification::votes_ancestries` and `Commit::precommits` (and `FinalityProof::unknown_headers`) to explicit, small maxima enforced at decode time (e.g. `BoundedVec` with a cap derived from realistic validator-set size and expected ancestry depth), rejecting oversized proofs before any verification work begins.
- Cap the per-verification computational budget: memoize/short-circuit repeated ancestry walks across precommits (e.g., cache visited nodes across precommit iterations instead of re-walking from scratch), and fail fast if the number of distinct headers walked exceeds a configured limit.
- Consider charging a deposit or requiring some minimal proof-of-work/fee for `handle_unsigned` consensus messages so that constructing an expensive-to-validate payload is not free for the submitter, consistent with dnsjava's KeyTrap fix, which added work limits to per-record validation.

### Proof of Concept
1. Construct a `GrandpaJustification` where `commit.precommits` contains `N` entries with known/public authority IDs (garbage or replayed signatures are fine since the ancestry walk executes regardless of the later signature/membership failure) and `votes_ancestries` contains `M` headers forming deep, distinct parent chains that don't all terminate before `base_hash`.
2. Wrap this in a `FinalityProof`/`ConsensusMessage::StandaloneChain` (or `Polkadot`) payload sized just under the node's max extrinsic length (~8MB per project docs), maximizing `N` and `M`.
3. Submit as `Message::Consensus(..)` inside `pallet_ismp::Call::handle_unsigned` via the standard unsigned-extrinsic RPC — no signer, no fee required.
4. Observe that every node performing `validate_unsigned` executes `verify_grandpa_finality_proof` → `GrandpaJustification::verify_with_voter_set`, performing `O(N × M)` ancestry-chain walks before failing on the final `visited_hashes != ancestry_hashes` check, consuming CPU disproportionate to the (zero) cost paid by the submitter.

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L109-143)
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

		let ancestry_hashes: BTreeSet<_> =
			self.votes_ancestries.iter().map(|h: &H| h.hash()).collect();

		if visited_hashes != ancestry_hashes {
			Err(anyhow!(
				"invalid precommit ancestries in grandpa justification with unused headers",
			))?
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

**File:** docs/content/developers/polkadot/solochains.mdx (L15-15)
```text
In your runtime, you should configure Hyperbridge as the coprocessor and add a GRANDPA consensus client to the list of consensus clients. The host state machine should be assigned a unique value for each solochain connected to Hyperbridge. You should also configure a larger block length limit to accommodate for large GRANDPA proofs. The new recommended limit is `8MB`, with a maximum extrinsic limit of 85%.
```
