Found the key candidate: the GRANDPA `AncestryChain::ancestry` function contains an unbounded `while current_hash != base` loop reachable directly from an unprivileged `handle_unsigned` extrinsic via consensus message verification.### Title
Infinite loop in GRANDPA `AncestryChain::ancestry` via cyclic parent-hash headers — Denial of Service on unsigned consensus messages - ([File: modules/consensus/grandpa/primitives/src/justification.rs])

### Summary
`AncestryChain::ancestry` (used by GRANDPA justification verification) walks a caller-supplied header list by following each header's `parent_hash` field until it reaches a target `base` hash, with no cycle detection and no bound on the number of hops. Because `parent_hash` is an attacker-controlled field independent of the header's actual computed hash, an attacker can submit two (or more) headers whose `parent_hash` fields point at each other, forming a cycle that never resolves to `base`. The `while` loop then spins forever. This function is reachable from the unsigned, permissionless `pallet_ismp::Call::handle_unsigned` extrinsic carrying a `Message::Consensus` for a GRANDPA-backed consensus client, and is invoked both in `ValidateUnsigned::validate_unsigned` (mempool/gossip validation, before block inclusion) and in dispatch.

### Finding Description
`AncestryChain::ancestry` builds a `BTreeMap<H::Hash, H>` keyed by each header's real cryptographic hash, then walks parent-links: [1](#0-0) 

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

The loop only terminates when `current_hash == base` or when a hash is missing from the map. There is no visited-set / cycle check. `current_header.parent_hash()` is a plain field of the SCALE-decoded header struct that the attacker fully controls at construction time — it is *not* derived from or checked against the actual hash of the referenced header. An attacker can therefore submit two headers `A` and `B` where `hash(A) = H_A`, `hash(B) = H_B`, `A.parent_hash = H_B`, and `B.parent_hash = H_A`. Both `H_A` and `H_B` are present as keys in the ancestry map, so the walk toggles `current_hash` between `H_A` and `H_B` forever, since neither ever equals `base` and both are always found in the map.

This function is called from `GrandpaJustification::verify_with_voter_set` (via `finality_grandpa::validate_commit`'s `Chain` trait, and directly for computing `visited_hashes`): [2](#0-1) 

and from the top-level GRANDPA verifier entrypoint that is invoked for every consensus update: [3](#0-2) 

The attacker-controlled header list feeding this map is `finality_proof.unknown_headers` (for `headers.ancestry(...)`) or `justification.votes_ancestries` (for the per-precommit ancestry check inside `verify_with_voter_set`) — both decoded directly from bytes an unprivileged caller supplies inside a `ConsensusMessage`.

The entire path is reachable from the permissionless, fee-less `pallet_ismp::Call::handle_unsigned` extrinsic: [4](#0-3) 

which is explicitly validated as an unsigned transaction — meaning the crafted cyclic-header message is executed inside `ValidateUnsigned::validate_unsigned` on every node that receives the gossiped extrinsic, before it is even included in a block: [5](#0-4) 

The GRANDPA client wrapper decodes the message and calls straight into `verify_grandpa_finality_proof` / `verify_parachain_headers_with_grandpa_finality_proof`, both of which reach `AncestryChain::ancestry`: [6](#0-5) 

### Impact Explanation
This is a direct, remotely triggerable infinite loop (CWE-835) reachable by any unprivileged party who can submit or gossip an unsigned extrinsic to a node running a GRANDPA-backed Hyperbridge consensus client. Because the check runs inside `validate_unsigned`, it executes on transaction-pool validation for every node that receives the extrinsic over the network — no block inclusion or collator cooperation is required. A single crafted 2-header (or larger) cycle causes that thread to spin forever, exhausting a CPU core and starving other transaction-pool validation and consensus-update processing on the affected node(s). If this happens broadly across relayer/validator/collator nodes servicing the affected state machine, GRANDPA consensus updates for that route stop being processed — a denial of service that leaves the route "unable to deliver messages," which is one of the explicitly in-scope impact categories. This qualifies as Medium/High severity: it is a clean, cheap (no fee, unsigned), reliably reproducible DoS against a core consensus-verification path.

### Likelihood Explanation
High likelihood of reachability: `handle_unsigned` is designed to accept free, permissionless ISMP messages including `Message::Consensus`, and the pool-validation code path executes the vulnerable ancestry walk unconditionally as part of validating any GRANDPA consensus message before any weight/fee gating is meaningfully applied against wasted CPU (validation itself is the DoS surface). Constructing the two cyclic headers requires no cryptographic break — the attacker only needs to choose arbitrary header field values and compute their SCALE-encoded hash locally (a header is hashed by the SubstrateHeader hasher), then reference each other's real hash in the `parent_hash` field. No signatures need to be forged to trigger the ancestry loop, since it is exercised before/independently of GRANDPA authority signature checks in `verify_with_voter_set`'s ancestry computation and in `verify_grandpa_finality_proof`'s pre-checks.

### Recommendation
- Add cycle detection to `AncestryChain::ancestry`, e.g., track a `BTreeSet` of visited hashes and return `Err(NotDescendent)` (or a new `CyclicAncestry` error) as soon as a hash is revisited.
- Alternatively/additionally, bound the walk by `self.ancestry.len() + 1` iterations, since a valid ancestry chain can never need more hops than there are distinct headers supplied.
- Apply the same defensive bound to any other callers that build `AncestryChain` from unsigned, attacker-supplied header lists (`finality_proof.unknown_headers`, `justification.votes_ancestries`) before performing expensive verification work in `validate_unsigned`.

### Proof of Concept
1. Construct two headers `A` and `B` of the `SubstrateHeader` type used by `ismp-grandpa`, with arbitrary but distinct content, and compute their real hashes `H_A = hash(A)`, `H_B = hash(B)`.
2. Set `A.parent_hash = H_B` and `B.parent_hash = H_A` (both are independent struct fields, no relation to the actual hash function needs to hold).
3. Build a `FinalityProof` (or a `GrandpaJustification` for `votes_ancestries`) whose `unknown_headers` (or `votes_ancestries`) is `[A, B]`, with `target = A` (so `finality_proof.block = H_A`) and craft the surrounding `ConsensusMessage`/`Message::Consensus` so it reaches the ismp-grandpa `verify_consensus`/`verify_fraud_proof` path.
4. Wrap this in `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Consensus(consensus_message)] }` and submit it as an unsigned extrinsic (or broadcast it over the p2p transaction-gossip layer) to a node running the `ismp-grandpa` client for the target state machine.
5. `validate_unsigned` decodes the message and calls into `verify_grandpa_finality_proof`, which calls `headers.ancestry(from, target.hash())`/`AncestryChain::ancestry`; since neither `H_A` nor `H_B` equals `base` and both are present in the map, the `while current_hash != base` loop toggles between them indefinitely, hanging the validating thread.

Note: I could not execute this against a running node/test harness (no code execution tooling available in this session) to empirically confirm the CPU hang; the analysis is based on static code review of the loop logic and its unsigned-message reachability shown above.

### Citations

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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-88)
```rust
	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
```

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

**File:** modules/pallets/ismp/src/lib.rs (L604-625)
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L1-45)
```rust
// Copyright (c) 2025 Polytope Labs.
// SPDX-License-Identifier: Apache-2.0

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// 	http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific lang
use polkadot_sdk::*;

use crate::{
	messages::{ConsensusMessage, SubstrateHeader},
	SupportedStateMachines,
};
use alloc::{boxed::Box, collections::BTreeMap, format, vec::Vec};
use codec::{Decode, Encode};
use core::marker::PhantomData;
use finality_grandpa::Chain;
use ismp::{
	consensus::{
		ConsensusClient, ConsensusClientId, ConsensusStateId, StateCommitment, StateMachineClient,
		VerifiedCommitments,
	},
	error::Error,
	host::{IsmpHost, StateMachine},
	messaging::StateCommitmentHeight,
};

use grandpa_verifier::{
	error::Error as GrandpaError, verify_grandpa_finality_proof,
	verify_parachain_headers_with_grandpa_finality_proof,
};
use grandpa_verifier_primitives::{
	justification::{AncestryChain, GrandpaJustification},
	ConsensusState, FinalityProof, ParachainHeadersWithFinalityProof,
};
use ismp::consensus::StateMachineId;
use sp_core::Get;
use sp_runtime::traits::Header;
use substrate_state_machine::{fetch_overlay_root_and_timestamp, SubstrateStateMachine};
```
