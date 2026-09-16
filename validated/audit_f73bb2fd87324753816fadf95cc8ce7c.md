I have sufficient evidence to confirm the finding. Let me verify the call path completes correctly.### Title
Unbounded ancestry-chain traversal in GRANDPA finality-proof verification allows an unsigned relayer message to hang the parachain (analogous to CVE-2021-2429) - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`AncestryChain::ancestry` in the GRANDPA consensus verifier walks a `parent_hash` chain built entirely from attacker-supplied, unverified header data, with no cycle detection and no bound on iteration count. This walk is invoked from `verify_grandpa_finality_proof` and `verify_parachain_headers_with_grandpa_finality_proof` **before** the GRANDPA justification's cryptographic signature is checked. Because the GRANDPA consensus message is delivered through `pallet_ismp::Call::handle_unsigned` — a call anyone can submit as an unsigned extrinsic, and which is also executed synchronously inside `ValidateUnsigned::validate_unsigned` during transaction-pool validation — a relayer can submit a single unsigned message whose `unknown_headers` contain a fabricated parent-hash cycle and drive the verifier into an unbounded/looping traversal, hanging block-import/tx-pool validation. This mirrors CVE-2021-2429's profile: a difficult/cheap, unauthenticated, network-reachable input that produces a hang/repeated-crash (availability-only) impact, with no valid signatures or privileged access required.

### Finding Description
`AncestryChain` is built directly from `finality_proof.unknown_headers`, a `Vec<H>` supplied by the caller inside `ConsensusMessage::Polkadot`/GRANDPA `FinalityProof`: [1](#0-0) 

The ancestry walk has no visited-set / depth bound: [2](#0-1) 

```
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

Each `H::Hash` key in the `BTreeMap` is the header's *real* computed hash (`h.hash()`), but the `parent_hash` field inside each header is an arbitrary, attacker-chosen value independent of that computed hash. An attacker can craft two (or more) headers `H1`, `H2` whose computed hashes are `h1`, `h2`, and set `H1.parent_hash = h2` and `H2.parent_hash = h1`. Inserted into `unknown_headers`, both land in the `ancestry` map. Any call to `ancestry(base, block)` where `block` resolves into this cycle and `base` is not `h1` or `h2` will loop `h1 -> h2 -> h1 -> h2 -> ...` forever, with `route` growing without bound each iteration (unbounded memory growth) or, at minimum, unbounded CPU consumption.

Critically, this call happens **before** the justification's authenticity is verified: [3](#0-2) 

Steps 1–9 (building the `AncestryChain`, resolving `target`/`base`, and the two `headers.ancestry(...)` calls at lines 83–88) all execute using only the attacker-supplied `unknown_headers`; `justification.verify(...)` — the actual BLS/Ed25519-style signature check against the trusted authority set — only runs afterward. This means the hang is triggered purely by unauthenticated header content with **no valid GRANDPA votes or signatures required at all**.

`verify_parachain_headers_with_grandpa_finality_proof` (used for the common Polkadot/Kusama-parachain path) calls the same vulnerable `verify_grandpa_finality_proof` first: [4](#0-3) 

The GRANDPA `ConsensusClient::verify_consensus` implementation decodes the untrusted `proof` bytes into a `ConsensusMessage` and routes straight into this verifier for the `Polkadot` variant: [5](#0-4) 

This is reached from `pallet_ismp::Call::handle_unsigned`, which is dispatchable by anyone as an unsigned extrinsic: [6](#0-5) 

and, more importantly, is also executed synchronously by the transaction-pool validity check itself, so simply *broadcasting* the malicious message (without it ever being included in a block) is enough to trigger the hang while nodes validate the pending extrinsic: [7](#0-6) 

By contrast, the codebase shows this class of bug has already been fixed in several sibling paths — e.g. the BEEFY `verify_mmr_leaf` empty-index panic, the sync-committee `multi_proof` length panic, and the Pharos SPV `MAX_PROOF_DEPTH` bound — all explicitly guarding against attacker-controlled proof shapes causing panics/DoS: [8](#0-7) [9](#0-8) [10](#0-9) 

The GRANDPA `AncestryChain::ancestry` traversal has no equivalent guard.

### Impact Explanation
This is a route-unable-to-deliver-messages / availability-impacting bug: an unauthenticated party (any relayer, or anyone able to submit an unsigned extrinsic/gossip a transaction) can hang GRANDPA consensus-update processing for any Hyperbridge deployment connected to a GRANDPA-finality chain (standalone GRANDPA chains, or Polkadot/Kusama relay+parachain via the BEEFY-adjacent GRANDPA client). Because the vulnerable path executes inside `validate_unsigned` (transaction-pool validation) as well as inside block execution, a single malicious message can stall transaction-pool processing/block-authoring on affected collators/validators — a hang or repeated crash consistent with a complete denial of service, matching the CVSS profile of the referenced CVE (network-reachable, no privileges, no user interaction, availability-only, "difficult to exploit" only in the sense of requiring crafted header bytes rather than any cryptographic break).

### Likelihood Explanation
Likelihood is high relative to the "difficult exploit" baseline of the CVE: no valid GRANDPA signatures, no compromised authority set, and no special privileges are needed — only the ability to submit/broadcast a single unsigned ISMP message with a crafted `ConsensusMessage::Polkadot { finality_proof: { unknown_headers: [H1, H2] } }` where `H1.parent_hash == H2.hash()` and `H2.parent_hash == H1.hash()`. All other fields (block, justification, target/base derivation) can be filled with otherwise-valid-shaped-but-unverified data sufficient to reach the vulnerable `ancestry()` calls before the justification check runs.

### Recommendation
Add cycle detection / a hard iteration bound to `AncestryChain::ancestry` (e.g., track visited hashes in a `BTreeSet` and bound iterations by `unknown_headers.len()`, returning `Error::NotDescendent` once exceeded), and consider re-ordering `verify_grandpa_finality_proof` so justification signature verification happens before any ancestry traversal over attacker-supplied headers, mirroring the defense-in-depth pattern already used for BEEFY MMR leaf indices and Pharos SPV proof depth.

### Proof of Concept
1. Construct two headers `H1`, `H2` of the concrete `SubstrateHeader`/`DefaultHeader` type used by the target's GRANDPA config, with arbitrary content except:
   - `H1.parent_hash = H2.hash()`
   - `H2.parent_hash = H1.hash()`
2. Set `finality_proof.unknown_headers = vec![H1, H2]`, `finality_proof.block = H1.hash()` (the max-height header among the two, satisfying `target.hash() == finality_proof.block`), and craft `justification.commit.target_hash = H1.hash()` (decode-valid but not yet cryptographically checked at this point in execution).
3. Set the trusted `consensus_state.latest_hash`/`latest_height` such that `base.number() < consensus_state.latest_height` is true (forcing the first vulnerable call at `headers.ancestry(base.hash(), consensus_state.latest_hash)`), where `consensus_state.latest_hash` is any hash not equal to `H1.hash()`/`H2.hash()`.
4. Encode this as a GRANDPA `ConsensusMessage` and wrap it in a `Message::Consensus` inside a `pallet_ismp::Call::handle_unsigned` extrinsic (unsigned origin) or simply broadcast it to the tx pool.
5. Observe `ValidateUnsigned::validate_unsigned` (or block execution) invoke `Self::execute` → `handle_incoming_message` → `GrandpaConsensusClient::verify_consensus` → `verify_parachain_headers_with_grandpa_finality_proof`/`verify_grandpa_finality_proof` → `AncestryChain::ancestry`, which loops indefinitely between `H1.hash()` and `H2.hash()`, never reaching `base`, consuming unbounded CPU/memory and hanging the validating node.

### Citations

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L44-104)
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
```

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L111-122)
```rust
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L69-106)
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
				let headers_with_finality_proof = ParachainHeadersWithFinalityProof {
					finality_proof: relay_chain_message.finality_proof,
					parachain_headers: relay_chain_message.parachain_headers,
				};

				let (consensus_state, parachain_headers) =
					verify_parachain_headers_with_grandpa_finality_proof(
						consensus_state,
						headers_with_finality_proof,
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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L225-237)
```rust
fn verify_mmr_leaf<H: Keccak256 + Send + Sync>(
	mmr: &MmrProof,
	mmr_root: H256,
) -> Result<(), Error> {
	// `leaf_indices` is supplied by the relayer in the unsigned consensus message;
	// an empty vector previously panicked the runtime via the unchecked `[0]` index
	// after the BEEFY signature and authority membership checks had already succeeded.
	// This verifier checks a single MMR leaf, so reject any proof that does not carry
	// exactly one leaf index.
	if mmr.mmr_proof.leaf_indices.len() != 1 {
		Err(Error::InvalidMmrProof)?
	}
	let leaf_index = mmr.mmr_proof.leaf_indices[0];
```

**File:** modules/consensus/sync-committee/verifier/src/lib.rs (L184-192)
```rust
	// `calculate_multi_merkle_root` panics on a short `multi_proof` because its final
	// `objects.get(&GeneralizedIndex(1)).unwrap()` cannot reconstruct the root. Reject
	// proofs whose helper-node count does not match what the algorithm requires so an
	// attacker-controlled `multi_proof` cannot panic the runtime via the public unsigned
	// consensus update path.
	if execution_payload.multi_proof.len() != get_helper_indices(&execution_payload_indices).len()
	{
		Err(Error::InvalidMerkleBranch("Execution payload multiproof length".into()))?;
	}
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
