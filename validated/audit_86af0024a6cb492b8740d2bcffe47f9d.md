## Title
Unbounded GRANDPA justification signature/ancestry verification enables CPU-exhaustion DoS via free unsigned transactions - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`GrandpaJustification::verify_with_voter_set` iterates over an attacker-supplied `commit.precommits: Vec<SignedPrecommit>` and `votes_ancestries: Vec<H>` with no upper bound on either collection's length, performing one ed25519 signature check and a linear ancestry-chain walk per precommit. This function is reached from `pallet_ismp::Call::handle_unsigned`, an **unsigned, feeless** extrinsic that "permits anyone [to] execute ISMP datagrams for free," and its cost is paid during `validate_unsigned` — i.e., on every node that receives the transaction via gossip, before it is even included in a block.

### Finding Description
`pallet-ismp`'s `handle_unsigned` call is explicitly documented as free and unsigned: [1](#0-0) 

Its `ValidateUnsigned::validate_unsigned` implementation calls `Self::execute(messages.clone())` directly, meaning full message execution — including consensus-proof verification — happens during mempool validation, which runs on every peer that receives the gossiped transaction, not just the block author: [2](#0-1) 

For a GRANDPA `ConsensusMessage`, this eventually reaches `GrandpaJustification::verify_with_voter_set`, which loops over `self.commit.precommits` doing a signature check (`check_message_signature`) and an ancestry-chain lookup for every entry, and additionally builds a `BTreeSet` from `self.votes_ancestries` (also attacker-controlled length): [3](#0-2) 

Unlike the BEEFY verifier's `check_participation_threshold` (bounding signature count relative to a known, fixed authority set) or the Pharos SPV verifier's `MAX_PROOF_DEPTH` guard, neither `precommits.len()` nor `votes_ancestries.len()` is bounded against `authorities.len()` or any fixed constant here — a search for any such cap (`MAX_VOTES`, `MAX_PRECOMMITS`, `precommits.len() <=`, etc.) turned up nothing. Grep search across the repo confirmed no such bound exists in this file, in contrast to comparable proof verifiers (`modules/consensus/pharos/primitives/src/spv.rs`, `evm/src/consensus/EcdsaBeefy.sol`) that do enforce depth/participation caps.

Because `Vec<Message>` and its nested `Vec<SignedPrecommit>`/`Vec<Header>` are only implicitly bounded by the outer extrinsic byte-length limit (a Substrate block's/extrinsic's default size ceiling, typically several MB), an attacker can pack thousands of forged (but self-consistently signed-format, even if cryptographically invalid) precommit/ancestry entries into a single justification. Each is walked with `check_message_signature` (ed25519 verification, ~µs-scale but nonzero) and an ancestry lookup (`ancestry_chain.ancestry(...)`, a `while` loop over a `BTreeMap`), producing O(n) to O(n²)-scale CPU work per submitted transaction — done for free, repeatedly, by every relaying node, since a rejected/invalid transaction can be resubmitted at will.

This class of bug — "a specially crafted input... allowed an attacker to trigger high CPU usage" reachable through an ordinary write path with no privileged access — is exactly the CVE-2022-1174 bug class cited in the external report, mapped here onto Hyperbridge's unsigned message-dispatch path (`handle_unsigned` / `HandlerV2`-equivalent consensus verification for GRANDPA).

### Impact Explanation
Since `handle_unsigned` is fee-less and unsigned, and its full cost (signature recovery + ancestry walking) is paid at `validate_unsigned` time on every node in the network (both collators and full nodes gossiping unsigned transactions), a single attacker can force disproportionate CPU consumption network-wide without spending any funds. Repeated submission of maximally-sized crafted justifications can degrade node responsiveness/liveness, delaying legitimate message delivery — a route-unable-to-deliver-messages/DoS impact under the given scope rules. This qualifies as at least Medium/High: it does not steal funds directly, but it can stall relaying/consensus-update processing network-wide at negligible attacker cost.

### Likelihood Explanation
Likelihood is high for the trigger (crafting and submitting an oversized unsigned transaction requires no privilege, no fee, and no special access — any RPC-reachable full node accepts it), but the achievable CPU cost per transaction is bounded by the outer extrinsic/block size limit, which I was **not able to fully confirm from the indexed code** (the search for `BlockLength`/`max_block`/extrinsic size constants for the parachain runtimes did not return the concrete numeric limits). Without that number, I cannot precisely quantify the worst-case number of precommits/ancestry headers an attacker could pack into one justification, so the exact severity multiplier (how many free ed25519 verifications/ancestry walks per submitted transaction) is uncertain and would need to be confirmed by reading the runtime's `System::BlockLength`/`BlockWeights` configuration directly.

### Recommendation
- Bound `commit.precommits.len()` and `votes_ancestries.len()` in `GrandpaJustification::verify`/`verify_with_voter_set` against a small constant multiple of the trusted `authorities.len()` (mirroring the BEEFY verifier's `check_participation_threshold` pattern) before any signature or ancestry work is performed.
- Reject the justification early (before signature verification / ancestry walking) if these bounds are exceeded, the same way `pallet_call_decompressor::decompress` now rejects an oversized claim before decompressing, and the way `spv.rs` enforces `MAX_PROOF_DEPTH` before descending the trie.
- Confirm and, if necessary, tighten the extrinsic/block-length ceiling that indirectly bounds `Vec<Message>`/`Vec<SignedPrecommit>`/`Vec<H>` sizes for the `handle_unsigned` unsigned-transaction path specifically, since this call bypasses normal fee-based spam deterrence.

### Proof of Concept
1. Construct a `GrandpaJustification<H>` whose `commit.precommits` contains `N` (e.g., tens of thousands) `SignedPrecommit` entries with distinct signatures/authority ids (need not be individually valid — each still costs a full `check_message_signature` ed25519 verification before being rejected), and whose `votes_ancestries` contains a matching number of distinct dummy headers to maximize the `BTreeSet`/ancestry-walk cost.
2. Wrap this justification as `ismp::messaging::ConsensusMessage` inside `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Consensus(...)] }` and encode it as an unsigned extrinsic, sized up to the chain's extrinsic/block length ceiling.
3. Submit/gossip the transaction to any node. `ValidateUnsigned::validate_unsigned` for `pallet_ismp` calls `Self::execute(messages.clone())` unconditionally [4](#0-3) , driving execution into `GrandpaJustification::verify_with_voter_set`'s unbounded loop over precommits/ancestries [5](#0-4) , consuming CPU proportional to `N` on every node that receives the gossip, at zero cost to the attacker (the call is fee-less and unsigned).
4. Repeat/resubmit variants to sustain elevated CPU load across the network.

### Citations

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

**File:** modules/pallets/ismp/src/lib.rs (L604-626)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L56-146)
```rust
	pub fn verify(&self, set_id: u64, authorities: &AuthorityList) -> Result<(), anyhow::Error> {
		// It's safe to assume that the authority list will not contain duplicates,
		// since this list is extracted from a verified relaychain header.
		let voters =
			VoterSet::new(authorities.iter().cloned()).ok_or(anyhow!("Invalid Authorities Set"))?;

		self.verify_with_voter_set(set_id, &voters)
	}

	/// Validate the commit and the votes' ancestry proofs.
	pub fn verify_with_voter_set(
		&self,
		set_id: u64,
		voters: &VoterSet<AuthorityId>,
	) -> Result<(), anyhow::Error> {
		use finality_grandpa::Chain;

		let ancestry_chain = AncestryChain::<H>::new(&self.votes_ancestries);

		match finality_grandpa::validate_commit(&self.commit, voters, &ancestry_chain) {
			Ok(ref result) if result.is_valid() => {
				if result.num_duplicated_precommits() > 0 ||
					result.num_invalid_voters() > 0 ||
					result.num_equivocations() > 0
				{
					Err(anyhow!("Invalid commit, found one of `duplicate precommits`, `invalid voters`, or `equivocations` {result:?}"))?
				}
			},
			err => {
				let result = err.map_err(|_| {
					anyhow!("[verify_with_voter_set] Invalid ancestry while validating commit!")
				})?;
				Err(anyhow!("invalid commit in grandpa justification: {result:?}"))?
			},
		}

		// we pick the precommit for the lowest block as the base that
		// should serve as the root block for populating ancestry (i.e.
		// collect all headers from all precommit blocks to the base)
		let base_hash = self
			.commit
			.precommits
			.iter()
			.map(|signed| &signed.precommit)
			.min_by_key(|precommit| precommit.target_number)
			.map(|precommit| precommit.target_hash.clone())
			.expect(
				"can only fail if precommits is empty; \
				 commit has been validated above; \
				 valid commits must include precommits; \
				 qed.",
			);

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

		Ok(())
	}
```
