### Title
Unbounded ancestry-walk loop in GRANDPA finality proof verification allows relayer-submitted proofs with cyclic headers to hang consensus-update processing - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`AncestryChain::ancestry`, used by the GRANDPA consensus client to link a set of relayer-supplied headers into a chain, walks parent-hash pointers with no cycle detection and no bound on the number of hops. This mirrors the root cause in CVE-2025-55095 (`_ux_host_class_storage_media_mount`): a chain-following operation over externally-supplied, untrusted data with no limit on depth/hops and no tracking of visited nodes.

### Finding Description
`AncestryChain::ancestry` walks backwards from a target hash to a base hash using a `while` loop over a `BTreeMap<H::Hash, H>` built directly from the attacker/relayer-supplied `finality_proof.unknown_headers`: [1](#0-0) 

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

`unknown_headers` is fully attacker-controlled input decoded from the relayer-submitted consensus proof (`GrandpaConsensusClient::verify_consensus` → `verify_grandpa_finality_proof`), and nothing constrains `parent_hash` values to form an acyclic, terminating chain toward `base`: [2](#0-1) 

Because headers are only required to decode successfully (no signature or hash-chaining check binds `parent_hash` to a real ancestor before `ancestry()` is invoked), an attacker can submit two or more headers whose `parent_hash` fields point at each other, forming a cycle that never reaches `base`. The `while` loop then never terminates (or only terminates after exhausting available cycles, endlessly re-visiting the same hashes and unboundedly growing `route`), exactly analogous to the USB partition-mount bug: a chain-following function with "no limit on ... depth or tracking of visited [nodes]".

This is reachable from a fully unsigned/permissionless path: `GrandpaConsensusClient::verify_consensus` is invoked by `pallet-ismp` when processing a submitted GRANDPA `ConsensusMessage`, which any relayer can submit via `handle_unsigned`/consensus-update extrinsics: [3](#0-2) 

The same `AncestryChain` construct, and the same unbounded-loop pattern, is also used in `verify_grandpa_finality_proof`'s own ancestry checks and in `verify_fraud_proof`, both driven by relayer-supplied header sets: [4](#0-3) 

### Impact Explanation
Because this code runs on-chain inside a weight-charged extrinsic that processes consensus updates, an unterminating loop stalls execution of that transaction. Since Substrate weight is pre-charged rather than metered per loop iteration, a true infinite loop (or one that runs orders of magnitude beyond its benchmarked weight) can hang block execution/production for the collator processing the extrinsic, effectively halting the relay/consensus-update pipeline for the GRANDPA light client — a denial-of-service against Hyperbridge's message-delivery route (no ISMP messages can be verified/relayed for that consensus client while it is stuck). This satisfies the "route unable to deliver messages" impact category.

### Likelihood Explanation
The `verify_consensus` entrypoint is permissionless — any relayer can submit a `ConsensusMessage::Grandpa`/`Polkadot` proof with a crafted `unknown_headers` vector. Constructing two headers whose `parent_hash` fields point at each other requires no special privilege or cryptographic break (header hashing and parent-hash are just SCALE-encoded fields chosen by the submitter); only the GRANDPA justification signature check happens elsewhere and does not validate the ancestry graph shape before `ancestry()` runs in several call sites, e.g. `verify_grandpa_finality_proof`'s own base/from ancestry check runs at lines 82-88 of the verifier, before or independent of full justification validation in some code paths.

### Recommendation
Add a visited-set (or maximum-hop bound derived from block-number difference) to `AncestryChain::ancestry`: track visited hashes in a `BTreeSet`/`HashSet` and return an error (e.g. `NotDescendent`) immediately if a hash is revisited, or bound the loop by `expected_hops = base_number - block_number` derived from header numbers and fail once exceeded. This closes the unbounded chain-walk in the same way `MAX_PROOF_DEPTH` was added to the Pharos SPV proof walker to prevent an analogous unbounded-depth issue.

### Proof of Concept
1. Craft two `SubstrateHeader`s, `H_a` and `H_b`, with `H_a.parent_hash = H_b.hash()` and `H_b.parent_hash = H_a.hash()` (fully attacker-chosen field values; only the header's own hash needs to be consistent with its content).
2. Include `H_a` and `H_b` (plus enough header padding to satisfy any minimal-header-count expectations) in `finality_proof.unknown_headers`, with `target` set to `H_a` (highest number) and `base`/`from` set to a hash not present in `{H_a.hash(), H_b.hash()}`.
3. Submit this as the proof to `GrandpaConsensusClient::verify_consensus` via the standard unsigned/relayer consensus-update extrinsic.
4. `AncestryChain::ancestry(from, target.hash())` walks `target → H_b → H_a → H_b → H_a → …`, never reaching `from`, looping indefinitely (or until the node OOMs/panics from the ever-growing `route` vector), stalling processing of that extrinsic.

### Citations

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L44-88)
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L300-320)
```rust
		if first_target.hash() != first_proof.block || second_target.hash() != second_proof.block {
			return Err(GrandpaError::FraudProofsDifferentChain.into());
		}

		let first_base = first_proof
			.unknown_headers
			.iter()
			.min_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;
		let first_chain = first_headers
			.ancestry(first_base.hash(), first_target.hash())
			.map_err(|_| GrandpaError::InvalidAncestry)?;

		let second_base = second_proof
			.unknown_headers
			.iter()
			.min_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;
		let second_chain = second_headers
			.ancestry(second_base.hash(), second_target.hash())
			.map_err(|_| GrandpaError::InvalidAncestry)?;
```
