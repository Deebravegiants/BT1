### Title
BEEFY consensus proof verification performs unbounded ECDSA recoveries for free via the unsigned `handle_unsigned` extrinsic — ([File: modules/consensus/beefy/verifier/src/lib.rs])

### Summary
`verify_mmr_update_proof` in the BEEFY verifier checks only a *lower bound* on the number of signatures in a submitted consensus proof (the supermajority threshold), never an *upper bound*. Because `pallet-ismp::handle_unsigned` is an unsigned extrinsic whose full message execution (including this verifier call) runs inside `ValidateUnsigned::validate_unsigned` — for free, on every full node that receives the gossiped transaction, before any fee or block-inclusion cost is paid — an attacker can submit consensus messages carrying an arbitrarily large signature array to force expensive `secp256k1_recover` work network-wide, repeatedly, at zero cost. This mirrors CVE-2023-3153's root cause: a hot path reachable by an unprivileged actor performs unbounded/expensive work with no rate limit on invocation.

### Finding Description
`pallet_ismp::Pallet::<T>::handle_unsigned` is deliberately free and unsigned (`ensure_none(origin)`), documented as "Execute the provided batch of ISMP messages for free with valid proofs" [1](#0-0) . Its `ValidateUnsigned::validate_unsigned` implementation calls `Self::execute(messages.clone())` — i.e., it *fully executes* the message batch, including consensus proof verification, just to decide mempool validity [2](#0-1) . This runs on every node that receives the transaction over the network, not just the block author, and it runs for a fee-less unsigned transaction.

For a `Message::Consensus` targeting the BEEFY consensus client, this routes to `update_client` → `consensus_client.verify_consensus` [3](#0-2) , which for BEEFY calls `verify_mmr_update_proof`:

```
let signatures_length = mmr.signed_commitment.signatures.len();
...
if !check_participation_threshold(signatures_length as u32, authority_set.len) {
    return Err(Error::SuperMajorityRequired);
}
...
for sig in mmr.signed_commitment.signatures.iter() {
    let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)...
``` [4](#0-3) 

`check_participation_threshold` only enforces `len >= (2*total/3)+1` — a floor, not a ceiling: [5](#0-4) 

There is no check that `signatures_length` is bounded by (or even close to) `authority_set.len`. An attacker can therefore submit a consensus message whose `signatures` vector contains far more entries than the real authority set (e.g., duplicated/garbage entries with arbitrary `authorityIndex` values), and the verifier will perform one `secp256k1_recover` (an expensive elliptic-curve operation) per entry *before* the subsequent Merkle multi-proof membership check (which would ultimately reject the forged/duplicated indices) is reached. The equivalent EVM verifier has the identical unbounded-loop pattern in `EcdsaBeefy.sol::verifyMmrUpdateProof` [6](#0-5) , but there gas metering naturally throttles the attack; on the Substrate side there is no equivalent cost, since the extrinsic is unsigned and the expensive work happens during (free) validation, not just execution.

The pool-level defenses that exist — `provides` tag dedup and `longevity: 25` — do not mitigate this: each submission can carry a distinct `consensus_proof` (hence a distinct `provides` hash) via trivial nonce/garbage variation, so the transaction pool treats each flood submission as a unique, valid-until-included transaction [7](#0-6) . Nothing rate-limits how many such (ultimately-invalid) large-signature-array proofs a peer can submit per unit time, nor caps the size of the signature array itself.

### Impact Explanation
This is a network-wide computational Denial of Service: unprivileged relayers (or any peer able to submit unsigned transactions/gossip) can force every Hyperbridge collator/full node to repeatedly perform O(n) expensive ECDSA recoveries for free, degrading block production and consensus-client liveness across the network — directly analogous to CVE-2023-3153's "attacker can cause a denial of service...including on deployments with [rate-limiting] enabled and properly configured" (CVSS 5.3, availability-only impact, network vector, no privileges/UI required). It does not by itself corrupt state (the forged proof still fails the Merkle membership check afterward), but it can stall message delivery for the BEEFY-anchored chains, which blocks routes from delivering messages — one of the explicitly in-scope impacts.

### Likelihood Explanation
High likelihood of triggerability: the path is reachable by a single unsigned/unauthenticated submission (`handle_unsigned`) carrying a `Message::Consensus` for the BEEFY consensus state — no signed origin, fee, or special privilege required. The only constraint is that consensus messages for this consensus ID must actually pass `IsmpCallFilter` on the runtime side (Gargantua/Nexus route BEEFY updates through `pallet-beefy-consensus-proofs` rather than raw `handle_unsigned`, per `IsmpCallFilter` [8](#0-7) ) — meaning on those specific runtimes the raw `handle_unsigned` BEEFY path is blocked, but the same unbounded-signature-array issue would still apply wherever the naive BEEFY verifier's `verify_consensus`/`verify_mmr_update_proof` is reachable via an unsigned/free extrinsic path (e.g., other chains configuring `ismp_beefy`/naive BEEFY directly via `handle_unsigned`, or the `PROOF_TYPE_NAIVE` branch inside `pallet-beefy-consensus-proofs::verify_and_apply`, which is itself dispatched via an extrinsic and still runs the same unbounded loop). I was not able to fully confirm within the available context whether `pallet-beefy-consensus-proofs`'s dispatch call is itself signed/fee-paying or unsigned/free on every deployed runtime — this should be verified before treating the finding as universally applicable across all configured chains.

### Recommendation
- Enforce an explicit upper bound on `mmr.signed_commitment.signatures.len()` (e.g., `<= authority_set.len`) before performing any `secp256k1_recover` calls in `verify_mmr_update_proof`, and reject early with `SuperMajorityRequired`/a new `TooManySignatures` error if exceeded.
- Deduplicate/validate `sig.index` values are within `[0, authority_set.len)` and unique before the recovery loop, so garbage/duplicate indices are rejected cheaply prior to any cryptographic work.
- Apply the same bound to the Solidity `EcdsaBeefy.sol::verifyMmrUpdateProof` for defense in depth even though gas metering partially mitigates it there.
- Consider moving expensive cryptographic verification out of `ValidateUnsigned::validate_unsigned` (or capping proof size more aggressively at the mempool boundary) so malformed/oversized proofs are rejected via cheap structural checks before full verification runs, consistent with the size-gate pattern already used in `pallet-call-decompressor` (`decompress_rejects_oversize_claim_before_decompressing`).

### Proof of Concept
Conceptual (not executed):
1. Craft a `Message::Consensus` targeting the BEEFY `consensus_state_id`, whose `consensus_proof` decodes to a `RelayChainProof`/`ConsensusMessage` containing a `signed_commitment.signatures` (or `votes`, in the Solidity ABI encoding) vector padded with thousands of syntactically-valid-but-bogus `(index, signature)` pairs — enough to satisfy `check_participation_threshold` while being far larger than the real authority set, but staying under the extrinsic/block size limit.
2. Submit this as an unsigned extrinsic via `Ismp::handle_unsigned([Message::Consensus(...)])` (or gossip it to the network).
3. Every full node that receives the extrinsic executes `validate_unsigned` → `execute` → `update_client` → `verify_mmr_update_proof`, performing one `secp256k1_recover` per padded signature entry before ultimately failing the Merkle authority-membership proof.
4. Repeat with trivially varied payloads (to keep `provides` tags unique and bypass pool dedup) to sustain the free CPU-consumption flood across the network.

I could not directly execute this PoC in this environment; the control-flow trace above is derived from reading `modules/pallets/ismp/src/lib.rs`, `modules/ismp/core/src/handlers/consensus.rs`, and `modules/consensus/beefy/verifier/src/lib.rs`, and should be validated with a running testnet/simnode before treating it as fully confirmed.

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

**File:** modules/pallets/ismp/src/lib.rs (L646-699)
```rust

			// No state machine was advanced by these messages. Build a content-unique
			// `provides` tag from the messages themselves so that distinct submissions
			// never collide in the transaction pool.
			//
			// A consensus message that doesn't advance a state machine (e.g. a
			// validator-set rotation during sync) previously mapped to an empty request
			// list via the catch-all arm. Every such message therefore produced an
			// identical `provides` tag and a fixed priority of 100, so the pool rejected
			// any two of them with "Priority is too low (100 vs 100)". Hashing the
			// consensus message (excluding the signer, so equivalent submissions from
			// different relayers dedupe) gives each update a unique tag.
			let mut has_consensus = false;
			let mut tags = messages
				.into_iter()
				.map(|message| match message {
					Message::Consensus(ConsensusMessage {
						consensus_proof,
						consensus_state_id,
						..
					}) => {
						has_consensus = true;
						vec![H256(sp_io::hashing::keccak_256(
							&(consensus_state_id, consensus_proof).encode(),
						))]
					},
					Message::FraudProof(FraudProofMessage { proof_1, proof_2, .. }) => vec![
						H256(sp_io::hashing::keccak_256(&proof_1)),
						H256(sp_io::hashing::keccak_256(&proof_2)),
					],
					Message::Request(RequestMessage { requests, .. }) => requests
						.into_iter()
						.map(|post| hash_request::<Pallet<T>>(&Request::Post(post.clone())))
						.collect::<Vec<_>>(),
					Message::Response(message) => message
						.requests()
						.iter()
						.map(|request| hash_request::<Pallet<T>>(request))
						.collect::<Vec<_>>(),
					Message::Timeout(message) => message
						.requests()
						.iter()
						.map(|request| hash_request::<Pallet<T>>(request))
						.collect::<Vec<_>>(),
				})
				.collect::<Vec<_>>();
			tags.sort();

			if tags.is_empty() {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}

			// this is so we can reject duplicate batches at the mempool level
			let msg_hash = sp_io::hashing::keccak_256(&tags.encode()).to_vec();
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L29-47)
```rust
pub fn update_client<H>(host: &H, msg: ConsensusMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	let consensus_client_id = host.consensus_client_id(msg.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized { consensus_state_id: msg.consensus_state_id },
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	let trusted_state = host.consensus_state(msg.consensus_state_id)?;
	host.is_consensus_client_frozen(msg.consensus_state_id)?;
	host.is_expired(msg.consensus_state_id)?;

	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-162)
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
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-261)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
}
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L122-163)
```text
    function verifyMmrUpdateProof(BeefyConsensusState memory trustedState, RelayChainProof memory relayProof)
        internal
        pure
        returns (BeefyConsensusState memory, bytes32)
    {
        uint256 sigLen = relayProof.signedCommitment.votes.length;
        uint256 latestHeight = relayProof.signedCommitment.commitment.blockNumber;
        Commitment memory commitment = relayProof.signedCommitment.commitment;
        if (
            commitment.validatorSetId != trustedState.currentAuthoritySet.id
                && commitment.validatorSetId != trustedState.nextAuthoritySet.id
        ) {
            revert UnknownAuthoritySet();
        }

        bool isCurrentAuthorities = commitment.validatorSetId == trustedState.currentAuthoritySet.id;
        AuthoritySetCommitment memory authoritySet =
            isCurrentAuthorities ? trustedState.currentAuthoritySet : trustedState.nextAuthoritySet;
        if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();

        uint256 payloadLength = commitment.payload.length;
        bytes32 mmrRoot;
        for (uint256 i = 0; i < payloadLength; i++) {
            if (commitment.payload[i].id == MMR_ROOT_PAYLOAD_ID && commitment.payload[i].data.length == 32) {
                mmrRoot = Bytes.toBytes32(commitment.payload[i].data);
            }
        }
        if (mmrRoot == bytes32(0)) revert MmrRootHashMissing();

        // verify the commitment
        bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
        MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
        for (uint256 i = 0; i < sigLen; i++) {
            Vote memory vote = relayProof.signedCommitment.votes[i];
            address authority = ECDSA.recover(commitmentHash, vote.signature);
            authorities[i] =
                MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
        }

        bool valid = MerkleMultiProof.VerifyProof(authoritySet.root, relayProof.proof, authorities, authoritySet.len);
        if (!valid) revert InvalidAuthoritiesProof();

```

**File:** parachain/runtimes/gargantua/src/lib.rs (L818-835)
```rust
pub struct IsmpCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for IsmpCallFilter {
	fn contains(call: &RuntimeCall) -> bool {
		use ::ismp::{host::IsmpHost, messaging::Message};
		match call {
			RuntimeCall::Ismp(pallet_ismp::Call::fund_message { .. }) => false,
			RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned { messages }) => {
				let host = Ismp::default();
				!messages.iter().any(|message| match message {
					Message::Consensus(consensus) =>
						host.consensus_client_id(consensus.consensus_state_id) ==
							Some(ismp_beefy::BEEFY_CONSENSUS_ID),
					_ => false,
				})
			},
			_ => true,
		}
	}
```
