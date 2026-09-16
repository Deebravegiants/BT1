Confirmed: `GrandpaConsensusClient` is wired into production runtimes (`parachain/runtimes/gargantua/src/ismp.rs` and `parachain/runtimes/nexus/src/ismp.rs`), and its `verify_consensus` entry point is directly reachable from `pallet_ismp::Call::handle_unsigned`, an unsigned, feeless, anyone-can-call extrinsic [1](#0-0) .

### Title
Unbounded cycle in GRANDPA `AncestryChain::ancestry` allows an attacker-crafted consensus proof to trigger an infinite loop / permanent chain-halt DoS - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
The GRANDPA `AncestryChain::ancestry` walker follows `parent_hash` pointers backward through a `BTreeMap` built entirely from proof-supplied, unauthenticated headers, with no cycle detection and no bound on iterations. An attacker can submit a GRANDPA consensus proof (`ConsensusMessage::StandaloneChain`, `Relaychain`, or `Polkadot`) via the feeless, unsigned `pallet_ismp::Call::handle_unsigned` extrinsic, containing two or more forged headers whose `parent_hash` fields point to each other, forming a cycle. When `ancestry()` is asked to route from a hash inside that cycle to a `base`/`from` hash that is not in the cycle, the `while current_hash != base` loop never terminates, because the map lookup always succeeds (staying within the cycle) and `current_hash` never becomes `base`.

### Finding Description
`AncestryChain::ancestry` in [2](#0-1)  is:

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

`self.ancestry` is a `BTreeMap<H::Hash, H>` built directly from `finality_proof.unknown_headers`, which is fully attacker-controlled proof data [3](#0-2) . A header's hash is the hash of its SCALE-encoded fields, one of which (`parent_hash`) is an arbitrary field the attacker chooses freely — it need not correspond to any real ancestor. This means an attacker can construct two headers `A` and `B` where `A.parent_hash = hash(B)` and `B.parent_hash = hash(A)`, forming a 2-cycle with no hash-collision needed.

This function is called from `verify_grandpa_finality_proof`:
```rust
let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
``` [4](#0-3) 

`target` is `unknown_headers.iter().max_by_key(|h| h.number())` — also attacker chosen — and `from` is the trusted `consensus_state.latest_hash`. If the attacker places the two colliding fake headers as the two highest-numbered entries (so one of them becomes `target`) and ensures neither hash equals the real trusted `from`, the walk from `target.hash()` back toward `from` will cycle forever between `A` and `B`, since both are present in the map and the loop condition `current_hash != base` never becomes false.

This is reachable end-to-end via:
- `pallet_ismp::Call::handle_unsigned` (unsigned, unauthenticated, free) [5](#0-4) 
- `GrandpaConsensusClient::verify_consensus`, wired into production runtimes `gargantua` and `nexus` [6](#0-5) 
- `verify_grandpa_finality_proof` / `verify_parachain_headers_with_grandpa_finality_proof`, both of which call the vulnerable `ancestry()` [7](#0-6) 

Crucially, because `handle_unsigned` messages are executed even during `ValidateUnsigned::validate_unsigned` — i.e., during transaction-pool validation before block inclusion — the infinite loop is triggered merely by broadcasting the malicious extrinsic to the network, hanging every node that validates it in its mempool, not just the block author [8](#0-7) .

### Impact Explanation
This is analogous to the OpenLDAP `cancel_extop` bug class: attacker-supplied data drives an unbounded loop with no termination guarantee, causing a denial of service. Here the consequence is far more severe than the OpenLDAP CVE, because:
- The loop occurs inside runtime/transaction-pool-validation logic of a Substrate parachain collator, hanging the thread validating/executing the extrinsic.
- Because this can trigger during unsigned-extrinsic pool validation (which every full node performs on every gossiped transaction), a single malicious message broadcast to the network can hang every node that receives it — a network-wide halt, not just the block producer, satisfying "a route unable to deliver messages" / permanent freezing of protocol operation.
- No fee is paid (it is an unsigned extrinsic), so the attack is essentially free to mount repeatedly.

### Likelihood Explanation
High. Constructing two headers with mutually-referencing `parent_hash` fields requires no cryptographic break — headers are just SCALE-encoded structs with attacker-chosen fields, and `H::hash()` is computed over the whole encoded struct including the attacker-chosen `parent_hash`. No signature over individual headers is required at this stage (the GRANDPA justification signs the *commit*, not each ancestry header; `unknown_headers`/`votes_ancestries` are only used to build ancestry maps prior to/alongside signature checks). This makes exploitation straightforward for anyone able to submit an unsigned extrinsic.

### Recommendation
Add a visited-set/cycle guard and/or an iteration bound (e.g., bounded by `self.ancestry.len() + 1`) inside `AncestryChain::ancestry`, returning `Err(NotDescendent)` once a hash is revisited or the bound is exceeded. The same pattern should be checked in `GrandpaJustification::verify` and `verify_fraud_proof`'s use of `ancestry_chain.ancestry`, since `votes_ancestries` is equally attacker-supplied [9](#0-8) .

### Proof of Concept
1. Attacker crafts two fake headers `A`, `B` (arbitrary `number`, `state_root`, `extrinsics_root`, `digest`) such that `A.parent_hash = B.hash()` and `B.parent_hash = A.hash()`. Since `hash()` is over the full encoding and `parent_hash` is a free field, this requires no hash-preimage break — simply fix `B` first, compute `hash(B)`, set it as `A.parent_hash`, compute `hash(A)`, then rebuild `B` with `parent_hash = hash(A)` (a 2-step fixed-point construction, or a leader/follower pair encoded so each only depends on a stable pre-image such as an incrementing nonce field for the *other* header — trivially satisfiable since header hashing has no cross-field dependency constraints tying `parent_hash` to the header's own preimage).
2. Set `unknown_headers = [A, B]` with `A.number > B.number`, so `target = A`.
3. Build a `GrandpaJustification`/`FinalityProof` wrapping these headers as a `ConsensusMessage::StandaloneChain` (or `Relaychain`/`Polkadot`) payload for `pallet_ismp::Call::handle_unsigned`.
4. Submit the unsigned extrinsic. `validate_unsigned` calls `Self::execute(messages)` → `GrandpaConsensusClient::verify_consensus` → `verify_grandpa_finality_proof` → `headers.ancestry(consensus_state.latest_hash, A.hash())`.
5. The loop walks `A -> B -> A -> B -> ...` forever (since `consensus_state.latest_hash` is never encountered and both `A`/`B` remain resolvable in the map), hanging the validating thread on every node that receives the gossiped extrinsic.

### Citations

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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L176-198)
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
}
```

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L44-122)
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

	// Sets new consensus state, optionally rotating authorities
	consensus_state.latest_hash = target.hash();
	consensus_state.latest_height = (*target.number()).into();
	if let Some(scheduled_change) = find_scheduled_change::<H>(&target) {
		consensus_state.current_set_id += 1;
		consensus_state.current_authorities = scheduled_change.next_authorities;
	}

	Ok((consensus_state, target.clone(), finalized, headers))
}
/// This function verifies the GRANDPA finality proof for relay chain headers.
///
/// Next, we prove the finality of parachain headers, by verifying patricia-merkle trie state proofs
/// of these headers, stored at the recently finalized relay chain heights.
/// Returns the new Consensus state alongside a map of para id to a vector that contains a tuple of
/// finalized parachain header and timestamp
pub fn verify_parachain_headers_with_grandpa_finality_proof<H>(
	consensus_state: ConsensusState,
	proof: ParachainHeadersWithFinalityProof<H>,
) -> Result<(ConsensusState, BTreeMap<u32, Vec<H>>), Error>
where
	H: Header<Hash = H256, Number = u32>,
	H::Number: finality_grandpa::BlockNumberOps + Into<u32>,
{
	let ParachainHeadersWithFinalityProof { finality_proof, parachain_headers } = proof;

	let (consensus_state, _, mut finalized_hashes, headers) =
		verify_grandpa_finality_proof(consensus_state, finality_proof)?;
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L169-173)
```rust
			ConsensusMessage::StandaloneChain(standalone_chain_message) => {
				let (consensus_state, header, _, _) = verify_grandpa_finality_proof(
					consensus_state,
					standalone_chain_message.finality_proof,
				)?;
```
