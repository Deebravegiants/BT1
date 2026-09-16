## Title
Unbounded-loop denial of service in GRANDPA finality proof verification via cyclic parent-hash chain in attacker-supplied ancestry headers - (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

## Summary
The GRANDPA consensus client's `AncestryChain::ancestry` function walks a peer-supplied set of headers by following `parent_hash` links from a target block back to a base block, with no cycle detection and no bound on the number of steps taken. An attacker who submits a crafted `FinalityProof`/`ConsensusMessage` containing headers whose parent-hash pointers form a cycle unrelated to the base/target pair can cause this walk to loop indefinitely, growing the `route` accumulator without bound — the same bug class as CVE-2026-58227 (TLS cross-signed certificate chain causing unbounded recursion), but expressed here as parent-hash traversal instead of issuer-certificate traversal.

## Finding Description
`AncestryChain::ancestry` in `modules/consensus/grandpa/primitives/src/justification.rs` is: [1](#0-0) 

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

`self.ancestry` is a `BTreeMap<Hash, Header>` built directly from the untrusted `votes_ancestries`/`unknown_headers` list supplied in the proof (`AncestryChain::new`). The loop only terminates when `current_hash == base` or when a hash is *not* present in the attacker-supplied map. If the attacker includes headers `C` and `D` such that `C.parent_hash() == D.hash()` and `D.parent_hash() == C.hash()` (mutually "cross-linked" headers, analogous to the cross-signed certificate pair in the OTP CVE), and the target-to-base walk passes into this `C ↔ D` cycle before reaching `base`, the loop alternates between `C` and `D` forever, since both are always found in the map and neither ever equals `base`. `route` grows unbounded on every iteration.

This function is called from `verify_grandpa_finality_proof` (used for both relay-chain and standalone-chain proofs) and from `GrandpaJustification::verify_with_voter_set`: [2](#0-1) 

This is reachable end-to-end from `pallet_ismp::Pallet::handle_unsigned`, an **unsigned, permissionless** extrinsic that executes attacker-supplied `Message::Consensus` payloads for free: [3](#0-2) 

and via `validate_unsigned`, which calls `Self::execute(messages)` — i.e., full consensus-proof verification, including the GRANDPA client path — is invoked during **transaction-pool validation itself**, before any fee or stake is charged: [4](#0-3) 

I could not find any bound on the number of headers accepted in `unknown_headers`/`votes_ancestries` (no `MAX_HEADERS`/`BoundedVec` cap was found in the GRANDPA primitives), nor any cycle-detection guard (e.g., a visited-set) in `AncestryChain::ancestry`. This contrasts with the Pharos SPV proof code in the same repo, which explicitly bounds proof depth (`MAX_PROOF_DEPTH`) precisely to defend against this class of issue — the GRANDPA ancestry walker has no equivalent bound.

## Impact Explanation
Because `handle_unsigned`/`validate_unsigned` is invoked by every full node's transaction pool on receipt of the extrinsic (before any fee is paid), a single crafted, free, unsigned transaction can drive any node running the GRANDPA consensus client into an unbounded loop that keeps allocating memory (`route.push`) and consuming CPU, with no termination condition beyond OOM or block-execution timeout. This can hang or crash validating/collating nodes, which is a route-availability/DoS impact for any consumer of GRANDPA-based light-client updates (parachain and standalone-chain relay paths), matching the "route unable to deliver messages" acceptance criterion.

## Likelihood Explanation
High likelihood of reachability: `handle_unsigned` is explicitly documented as callable by anyone ("Unsigned... permits anyone execute ISMP messages for free"), and the vulnerable code path is exercised both during mempool validation (`validate_unsigned`) and dispatch (`execute`). Constructing two headers with mutually pointing `parent_hash` fields requires no cryptographic break — GRANDPA header parent-hash fields are attacker-controlled input fields in `votes_ancestries`, and the ancestry-cycle check occurs before/independent of signature verification of the commit (the ancestry walk in `verify_grandpa_finality_proof` runs prior to `justification.verify(...)`).

## Recommendation
Add cycle detection and/or a hard bound on the number of steps taken in `AncestryChain::ancestry` (e.g., track visited hashes in a `BTreeSet` and return an error on revisit, and/or cap `route.len()` at `self.ancestry.len() + 1`, since a valid ancestry path can never be longer than the number of supplied headers). Additionally, enforce an explicit maximum on the number of headers accepted in `unknown_headers`/`votes_ancestries` before any traversal begins, mirroring the `MAX_PROOF_DEPTH` guard already used in `modules/consensus/pharos/primitives/src/spv.rs`.

## Proof of Concept
1. Craft two headers `C` and `D` (arbitrary otherwise-valid `Header` structures) such that `C.parent_hash() == D.hash()` and `D.parent_hash() == C.hash()`.
2. Craft a target header `T` whose `parent_hash()` points to `C.hash()`, and a base header `B` unrelated to `C`/`D`.
3. Submit `Message::Consensus(ConsensusMessage { consensus_proof: <FinalityProof containing [B, T, C, D] as unknown_headers/votes_ancestries>, .. })` via `pallet_ismp::Call::handle_unsigned`.
4. When `verify_grandpa_finality_proof`/`GrandpaJustification::verify` calls `AncestryChain::ancestry(B.hash(), T.hash())`, the walk reaches `C`, then alternates `C → D → C → D → …` indefinitely (since neither equals `B`), growing `route` without bound and never returning — hanging the validating node's `validate_unsigned`/`execute` call. [1](#0-0) [5](#0-4)

### Citations

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-103)
```rust
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
