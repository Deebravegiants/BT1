## Title
Infinite-loop DoS in GRANDPA ancestry traversal via attacker-crafted cyclic headers in a submitted consensus proof - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
The GRANDPA consensus-client's `AncestryChain::ancestry` function walks a chain of headers by following each header's `parent_hash` pointer through a `BTreeMap` built directly from the attacker-supplied `unknown_headers` field of a submitted `FinalityProof`. The traversal loop has no cycle/visited-set detection: it only checks whether the current hash exists as a key in the map, not whether it has already been visited. A relayer can submit a `Message::Consensus` proof whose `unknown_headers` contain two (or more) headers whose `parent_hash` fields point at each other, forming a cycle. When such a proof reaches `verify_grandpa_finality_proof`/`verify()`, the traversal never reaches the target `base` hash and loops forever, hanging the node executing the extrinsic — the same bug class as `matrix-js-sdk`'s `getRoomUpgradeHistory`, which infinitely recurses on a crafted predecessor cycle.

### Finding Description
`AncestryChain::ancestry` is implemented as: [1](#0-0) 

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

`self.ancestry` is a `BTreeMap<H::Hash, H>` built purely from `unknown_headers`, an attacker-controlled part of the submitted `FinalityProof`: [2](#0-1) 

Nothing enforces that `parent_hash` chains form an acyclic path back to `base`; a header's `hash()` and `parent_hash()` fields are independently attacker-chosen (the header struct is arbitrary, only later checked against justification signatures on the *target*, not on the internal ancestry graph). If the attacker sets header `A.parent_hash = hash(B)` and `B.parent_hash = hash(A)`, both `A` and `B` remain present in the map forever, so `while current_hash != base` never becomes false and the loop spins indefinitely.

This function is reachable from consensus-message processing:
- `verify_grandpa_finality_proof` calls `headers.ancestry(base.hash(), consensus_state.latest_hash)` and `headers.ancestry(from, target.hash())`, both fed by `AncestryChain::new(&finality_proof.unknown_headers)`: [3](#0-2) 
- This is invoked by the GRANDPA `ConsensusClient::verify_consensus`, driven by a decoded, attacker-submitted `ConsensusMessage` (`StandaloneChain` or `Relaychain` variants): [4](#0-3) 
- Consensus messages reach this path via the generic `handle_incoming_message` dispatcher used for any submitted `Message::Consensus`: [5](#0-4) 
- The same `AncestryChain`/`ancestry()` machinery also backs `GrandpaJustification::verify_with_voter_set`, both directly and via the external `finality_grandpa::validate_commit(..., &ancestry_chain)` call which itself invokes `Chain::ancestry` on attacker data: [6](#0-5) 

Any unprivileged relayer able to submit consensus/ISMP messages (e.g. via `pallet_ismp`'s unsigned/permissionless `handle_unsigned` message execution) can trigger this path with a crafted proof.

### Impact Explanation
Because there is no cycle detection, the `while` loop runs unbounded, consuming CPU without yielding, inside native runtime execution of an extrinsic. Substrate's weight metering does not interrupt mid-execution infinite loops in native code, so a validator/full node executing this extrinsic will hang, halting block production/import for that node. Since GRANDPA consensus-state updates gate all downstream state/membership proof verification for that counterparty chain, a stuck consensus-update path also permanently blocks delivery of any further cross-chain messages (post/get requests, responses, timeouts) routed through that light client — a route rendered permanently unable to deliver messages, and if triggered broadly across validating nodes, a chain-halting liveness failure.

### Likelihood Explanation
The attack requires only crafting two headers with mutually-referencing `parent_hash` fields inside the `unknown_headers` vector of a `FinalityProof`/`ConsensusMessage` and submitting it as a normal, permissionless consensus message — no privileged role, no valid justification signatures are needed to reach the vulnerable loop (the loop runs before/during traversal, prior to or during the point where full justification signature verification would otherwise reject the message). This mirrors exactly the reachability profile the JS-SDK advisory describes (untrusted party crafts a cyclic structure that a public traversal function walks without cycle protection).

### Recommendation
Add cycle/visited-set detection to `AncestryChain::ancestry` (and any other in-repo consumer of the same header map, including anywhere `finality_grandpa::Chain::ancestry` is exercised on attacker-supplied header sets): track visited hashes in a `BTreeSet`/`HashSet` and return `Err(NotDescendent)` immediately if a hash is revisited before reaching `base`. Additionally bound the traversal by the number of entries in `self.ancestry` (a chain can visit each header at most once), erroring out once that bound is exceeded.

### Proof of Concept
1. Craft two `SubstrateHeader` values `A` and `B` such that `A.parent_hash() == B.hash()` and `B.parent_hash() == A.hash()` (arbitrary field values are permitted; hashes are simply `blake2b` over the attacker-chosen header contents).
2. Build a `FinalityProof { block: A.hash(), unknown_headers: vec![A, B], justification: <any decodable justification bytes with target_hash == A.hash()> }` and wrap it as `ConsensusMessage::StandaloneChain(StandaloneChainMessage { finality_proof })`.
3. Submit this as a `Message::Consensus` via the normal permissionless message-handling entry point (`handle_incoming_message` → `GrandpaConsensusClient::verify_consensus` → `verify_grandpa_finality_proof`).
4. Execution reaches `headers.ancestry(from, target.hash())` in `modules/consensus/grandpa/verifier/src/lib.rs`; since `current_hash` (`hash(B)` → `hash(A)` → `hash(B)` → ...) is always present in the map and never equals `base`/`from` (chosen to be some third hash never linked into the cycle), the `while` loop in `modules/consensus/grandpa/primitives/src/justification.rs`'s `ancestry` never terminates, hanging the executing node.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L66-90)
```rust
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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L52-88)
```rust
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L169-212)
```rust
			ConsensusMessage::StandaloneChain(standalone_chain_message) => {
				let (consensus_state, header, _, _) = verify_grandpa_finality_proof(
					consensus_state,
					standalone_chain_message.finality_proof,
				)?;

				let slot_duration = SupportedStateMachines::<T>::get(consensus_state.state_machine)
					.ok_or(GrandpaError::SlotDurationNotSet(consensus_state.state_machine))?;
				let digest_result =
					fetch_overlay_root_and_timestamp(header.digest(), slot_duration)?;

				let height: u32 = (*header.number()).into();

				let state_id = consensus_state.state_machine;

				let intermediate = StateCommitmentHeight {
					commitment: StateCommitment {
						timestamp: digest_result.timestamp,
						overlay_root: Some(digest_result.ismp_digest.child_trie_root),
						state_root: header.state_root,
					},
					height: height.into(),
				};

				let mut state_commitments_vec = Vec::new();
				state_commitments_vec.push(intermediate);

				intermediates
					.insert(StateMachineId { state_id, consensus_state_id }, state_commitments_vec);

				Ok((consensus_state.encode(), intermediates))
			},

			ConsensusMessage::Relaychain(relay_chain_message) => {
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
