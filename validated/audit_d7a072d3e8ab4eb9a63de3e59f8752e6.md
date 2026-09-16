## Analog Found: Unbounded loop in GRANDPA ancestry walk causes indefinite hang on attacker-controlled headers

### Title
Infinite loop / hang in `AncestryChain::ancestry` reachable via unsigned GRANDPA consensus messages - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
The CVE-2019-2974 bug class is a low-privilege, network-reachable input that drives the target into an unbounded/looping computation resulting in a hang or crash (complete DoS), without needing any special credential. The Hyperbridge GRANDPA consensus verifier has a directly analogous defect: `AncestryChain::ancestry` walks a `parent_hash` pointer chain built entirely from attacker-supplied, unauthenticated header structs, and terminates only when it reaches a specific target hash. If the attacker submits two headers that reference each other as parent (a two-node cycle), the walk loops forever, and this call happens **before** any cryptographic signature check on the justification.

### Finding Description
`AncestryChain::ancestry` in [1](#0-0)  walks backwards from `block` to `base` following `parent_hash` pointers taken from a `BTreeMap<H::Hash, H>` built directly from the untrusted `finality_proof.unknown_headers` supplied in the message:

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

`AncestryChain::new` indexes headers purely by `header.hash()` [2](#0-1) . Nothing constrains `parent_hash` to actually be the hash of a "previous" header in any real chain — headers are just SCALE-decoded structs supplied by the caller. An attacker can therefore construct two headers `H1`, `H2` such that `H1.parent_hash() == hash(H2)` and `H2.parent_hash() == hash(H1)`, forming a 2-cycle. Since both `hash(H1)` and `hash(H2)` exist as keys in `self.ancestry`, the lookup at every step of the `while` loop succeeds, `current_hash` oscillates between the two hashes, and the loop never reaches `base` and never returns `Err` — it runs forever, appending to `route` without bound.

This function is invoked in `verify_grandpa_finality_proof` at [3](#0-2)  — critically, **before** the justification's cryptographic signature is checked (`justification.verify(...)` runs afterward, at line 91-93 of the same file). So no authentication gate protects this code path; a wholly unsigned, unauthenticated pair of crafted headers is enough to enter the loop.

`verify_grandpa_finality_proof` is the verification entrypoint for the GRANDPA `ConsensusClient::verify_consensus` implementation [4](#0-3) , which is dispatched from `pallet_ismp::Call::handle_unsigned`, an **unsigned** extrinsic that "permits anyone execute ISMP messages for free" [5](#0-4) . Worse, `validate_unsigned` for this call runs `Self::execute(messages.clone())` directly during **transaction-pool validation** [6](#0-5) , so the infinite loop is triggered merely by broadcasting the malicious extrinsic to the network — every node that receives and validates it before inclusion in a block hangs.

### Impact Explanation
Any single unsigned transaction can permanently hang the block-authoring/validation thread of any node running the GRANDPA consensus client (a fee-less, permissionless message dispatcher can reach it). This is a full denial of service of message delivery for the GRANDPA route, and because `validate_unsigned` executes the vulnerable path at the transaction-pool layer, it can hang nodes without ever landing in a block — a network-wide DoS vector reachable from a single relayed message, matching the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
Trivial and deterministic to trigger: constructing a two-header cycle only requires setting each header's `parent_hash` field to the hash of the other — no signatures, no economic cost beyond submitting one unsigned extrinsic, and no privileged role. This is directly analogous to the referenced MySQL CVE's "easily exploitable... low privileged attacker... complete DOS via hang."

### Recommendation
Bound the ancestry walk with a maximum iteration count (e.g., derived from `unknown_headers.len()`, since a legitimate chain visits each header at most once) and return an error if exceeded, mirroring the `MAX_PROOF_DEPTH` guard already applied elsewhere in the codebase (e.g., Pharos SPV proofs). Alternatively, track visited hashes in a set and reject on revisit before following the next `parent_hash` pointer, which both bounds the loop and rejects cyclic/malformed ancestries as invalid.

### Proof of Concept
1. Craft two `SubstrateHeader` values `H1`, `H2` where `H1.parent_hash = hash(H2)` and `H2.parent_hash = hash(H1)` (all other fields arbitrary/zeroed).
2. Build a `FinalityProof { block: hash(H_target), justification: <any bytes>, unknown_headers: vec![H1, H2, H_target, ...] }` where `H_target`'s number is the max, satisfying the `target.hash() == finality_proof.block` check.
3. Submit via `pallet_ismp::Call::handle_unsigned` wrapping a GRANDPA `ConsensusMessage`.
4. `validate_unsigned` (or `execute` on inclusion) calls `verify_grandpa_finality_proof`, which calls `headers.ancestry(from, target.hash())`; the walk enters the `H1`/`H2` cycle and never returns, hanging the calling thread indefinitely — before the justification signature is ever checked.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L161-167)
```rust
impl<H: HeaderT> AncestryChain<H> {
	/// Initialize the ancestry chain given a set of relay chain headers.
	pub fn new(ancestry: &[H]) -> AncestryChain<H> {
		let ancestry: BTreeMap<_, _> = ancestry.iter().cloned().map(|h: H| (h.hash(), h)).collect();

		AncestryChain { ancestry }
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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-88)
```rust
	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L155-214)
```rust
							},
						};

						state_commitments_vec.push(intermediate);
					}

					intermediates.insert(
						StateMachineId { state_id, consensus_state_id },
						state_commitments_vec,
					);
				}

				Ok((consensus_state.encode(), intermediates))
			},
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

				let parachain_headers = parachain_headers
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
