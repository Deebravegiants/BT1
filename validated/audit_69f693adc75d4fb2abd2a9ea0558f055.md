### Title
Unbounded, unmetered `handle_unsigned` message batches let an unsigned transaction force full (and repeated) expensive consensus/proof verification, enabling a free CPU-exhaustion DoS - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp::handle_unsigned` accepts an unbounded `Vec<Message>` from an unsigned/permissionless origin and its `ValidateUnsigned::validate_unsigned` implementation runs `Self::execute(messages.clone())` — a **full** execution of every message in the batch, including cryptographic consensus-proof verification (BEEFY/GRANDPA/BSC/Tendermint signature recovery, Merkle/MMR proof checks) — before the extrinsic is even accepted into a block. This mirrors the OpenDaylight CVE-2017-1000361 bug class: attacker-controlled input drives expensive processing/exception paths that consume disproportionate CPU on every node that has to validate it, and can be resubmitted at effectively no cost.

### Finding Description
`handle_unsigned` is declared as an unsigned, permissionless extrinsic: [1](#0-0) 

Its `validate_unsigned` implementation fully executes the message batch to compute the transaction's `provides`/`priority` tags: [2](#0-1) 

`Self::execute` decodes and processes **every** message in the vector via `handle_incoming_message`, which dispatches to consensus-client verification, request/response/timeout handling — all of this runs to completion (including signature recovery and Merkle-proof verification) purely to answer `validate_unsigned`: [3](#0-2) [4](#0-3) 

Consensus clients invoked from this path perform non-trivial cryptography per proof — e.g. BEEFY MMR/authority-set verification with ECDSA `secp256k1_recover` over every signature in the commitment, and Merkle multi-proof verification: [5](#0-4) 

Because `validate_unsigned` is invoked by every node in the network on receipt of the extrinsic (gossip, mempool re-validation on every new best-block, block-building), and Substrate's unsigned-extrinsic pipeline provides no fee/weight gate *before* this validation executes, a batch of `messages` can be made arbitrarily large (no `MaxMessages` bound was found guarding `Vec<Message>` in this pallet) or can pack many computationally expensive-but-ultimately-invalid consensus/request proofs. The `#[pallet::weight(weight())]` annotation only affects post-validation dispatch weight accounting; it does not bound the size/cost of the `messages` vector consumed during `validate_unsigned`, so the expensive verification work happens unconditionally and repeatedly (once per validation pass, potentially many times per block cycle across the network) regardless of whether the batch is ultimately accepted.

This is structurally the same bug class as the referenced advisory: adversary-supplied packets/messages that are technically well-formed but crafted to be maximally expensive to process, exercised through a permissionless entry point that lacks a cheap pre-check, driving unbounded CPU consumption across the network of validating nodes.

### Impact Explanation
An attacker can submit unsigned `handle_unsigned` extrinsics with large batches of consensus messages, or messages containing computationally expensive but invalid proofs, and gossip them network-wide. Every honest collator/full node validating the transaction pool will re-run full cryptographic verification (ECDSA recovery over many signatures, MMR/Merkle-proof checks, GRANDPA justification verification, etc.) for each of these unsigned transactions on every revalidation cycle, at zero cost to the attacker (unsigned extrinsics carry no fee). Sustained submission can degrade or stall block production and RPC responsiveness network-wide — a High-severity availability impact consistent with "Route unable to deliver messages" / protocol-wide DoS, matching the required impact categories.

### Likelihood Explanation
`handle_unsigned` is explicitly designed to be permissionless ("allows users execute ISMP datagrams for free, use with caution") and reachable directly from a single submitted extrinsic — no privileged role, governance, or prior state is required. Crafting oversized or maximally-expensive-yet-invalid message batches (e.g., large `Vec<Message>` of consensus proofs with many bogus signatures) is straightforward for any network participant, making this readily exploitable by an unprivileged relayer/attacker.

### Recommendation
- Add an explicit upper bound on `messages.len()` (and on nested proof sizes, e.g., BEEFY signature count / MMR proof depth) enforced as a *cheap* pre-check at the very start of `validate_unsigned`, before any cryptographic verification runs.
- Consider a lightweight, weight-proportional "cheap validity" pass (e.g., structural/size checks and decode-cost bounds) that runs in `validate_unsigned`, deferring full cryptographic verification to `pre_dispatch`/`execute` only after that cheap pass succeeds, so repeated mempool revalidation does not repeatedly pay the full cryptographic cost.
- Bound `MAX_CONSENSUS_MESSAGES_PER_TX`-style batching (already used on the relayer side, see `tesseract/consensus/bsc/src/host.rs`) at the protocol level inside the pallet itself, not just relayer-side convention.

### Proof of Concept
1. Construct an unsigned extrinsic `pallet_ismp::Call::handle_unsigned { messages }` where `messages` is a `Vec<Message>` containing, e.g., hundreds of `Message::Consensus` entries addressed to the BEEFY consensus client, each with a syntactically valid but maximal-size `signed_commitment.votes` array (many ECDSA signatures) that ultimately fails verification (e.g., wrong authority set participation).
2. Submit this extrinsic to the network via the unsigned RPC/gossip path (as demonstrated for legitimate messages in `parachain/simtests/src/pallet_ismp.rs:584-592` and `tesseract/messaging/integration-test/src/lib.rs:90-99`, which shows `handle_unsigned` messages propagating through `client.tx().create_unsigned(...)`).
3. Every node that receives the extrinsic invokes `ValidateUnsigned::validate_unsigned`, which calls `Self::execute(messages.clone())` → `handle_incoming_message` → BEEFY `verify_consensus` → `verify_mmr_update_proof`, performing `secp256k1_recover` for every signature in the batch before rejecting the (invalid) proof.
4. Repeat submission with new nonces/sentinel bytes (as shown feasible in `modules/pallets/testsuite/src/tests/pallet_ismp.rs:566-605`, where distinct consensus messages get unique `provides` tags and are individually revalidated) to keep forcing full re-verification across the network at negligible attacker cost, since the extrinsic is unsigned and free.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
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

**File:** modules/pallets/ismp/src/impls.rs (L40-57)
```rust
	pub fn execute(messages: Vec<Message>) -> Result<Vec<events::Event>, Error<T>> {
		let host = Pallet::<T>::default();

		let message_results = messages
			.iter()
			.map(|msg| handle_incoming_message(&host, msg.clone()))
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;

		let messages_with_weights = message_results
			.iter()
			.zip(messages)
			.map(|(result, message)| MessageWithWeight { message, weight: result.weight() })
			.collect::<Vec<_>>();
```

**File:** modules/ismp/core/src/handlers.rs (L86-100)
```rust
pub fn handle_incoming_message<H>(
	host: &H,
	message: Message,
) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	match message {
		Message::Consensus(consensus_message) => consensus::update_client(host, consensus_message),
		Message::FraudProof(fraud_proof) => consensus::freeze_client(host, fraud_proof),
		Message::Request(req) => request::handle(host, req),
		Message::Response(resp) => response::handle(host, resp),
		Message::Timeout(timeout) => timeout::handle(host, timeout),
	}
}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-176)
```rust
pub fn verify_mmr_update_proof<H: Keccak256 + EcdsaRecover + Send + Sync>(
	mut trusted_state: ConsensusState,
	mmr: MmrProof,
) -> Result<(ConsensusState, H256), Error> {
	let signatures_length = mmr.signed_commitment.signatures.len();
	let latest_height = mmr.signed_commitment.commitment.block_number;

	if trusted_state.latest_beefy_height >= latest_height {
		return Err(Error::StaleHeight {
			trusted_height: trusted_state.latest_beefy_height,
			current_height: latest_height,
		});
	}

	let commitment = mmr.signed_commitment.commitment.clone();

	// Pick the authority set the commitment claims to be signed under, then judge
	// participation against that set alone.
	let authority_set = if commitment.validator_set_id == trusted_state.current_authorities.id {
		&trusted_state.current_authorities
	} else if commitment.validator_set_id == trusted_state.next_authorities.id {
		&trusted_state.next_authorities
	} else {
		return Err(Error::UnknownAuthoritySet { id: commitment.validator_set_id });
	};

	if !check_participation_threshold(signatures_length as u32, authority_set.len) {
		return Err(Error::SuperMajorityRequired);
	}

	let mmr_root_data = commitment
		.payload
		.get_raw(&MMR_ROOT_PAYLOAD_ID)
		.ok_or(Error::MmrRootHashMissing)?;

	if mmr_root_data.len() != 32 {
		return Err(Error::InvalidMmrRootHashLength { len: mmr_root_data.len() });
	}
	let mmr_root = H256::from_slice(mmr_root_data);

	let commitment_hash = H::keccak256(&commitment.encode());
	let mut authority_leaves: Vec<[u8; 32]> = Vec::new();
	let mut authority_indices = Vec::new();

	for sig in mmr.signed_commitment.signatures.iter() {
		let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)
			.map_err(|_| Error::FailedToRecoverPublicKey)?;

		let hashed_uncompressed = H::keccak256(&uncompressed);

		let mut eth_address = [0u8; 20];
		eth_address.copy_from_slice(&hashed_uncompressed.as_ref()[12..]);

		let authority_address_hash = H::keccak256(&eth_address);

		authority_leaves.push(authority_address_hash.into());
		authority_indices.push(sig.index as usize);
	}

	let merkle_proof = MerkleProof::<MerkleHasher<H>>::new(mmr.authority_proof.clone());

	let valid = merkle_proof.verify(
		authority_set.keyset_commitment.into(),
		&authority_indices,
		&authority_leaves,
		authority_set.len as usize,
	);

	if !valid {
		Err(Error::InvalidAuthoritiesProof)?;
	}

```
