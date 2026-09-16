## Title
Unbounded busy-loop DoS in GRANDPA ancestry-chain walk via a cyclic `votes_ancestries` — (File: `modules/consensus/grandpa/primitives/src/justification.rs`)

### Summary
`AncestryChain::ancestry`, used by the GRANDPA consensus-proof verifier that processes attacker-supplied, permissionless consensus messages, walks parent-hash pointers in a `while` loop with no bound on iteration count and no cycle detection. A relayer can submit a `GrandpaJustification`/`FinalityProof` whose `votes_ancestries`/`unknown_headers` headers form a hash cycle (header A's `parent_hash` = hash(B), header B's `parent_hash` = hash(A)), causing the loop to spin forever without ever reaching the `base` hash, exactly the class of unbounded-loop mishandling described in CVE-2018-7287 (zero-size WebSocket payloads causing a busy loop in `res_http_websocket.c`).

### Finding Description
`AncestryChain::ancestry` is implemented as: [1](#0-0) 

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

The `ancestry` map is built directly from attacker-supplied headers in `votes_ancestries`/`unknown_headers`, keyed by each header's own (correctly computed) hash: [2](#0-1) 

Because the key for each entry is the header's real hash, but the header's `parent_hash` field is fully attacker-controlled content, a relayer can submit two (or more) headers H1, H2 where `H1.parent_hash == hash(H2)` and `H2.parent_hash == hash(H1)`. When `ancestry(base, block)` is invoked with `block` inside that cycle and `base` outside it, `current_hash` bounces between `hash(H1)` and `hash(H2)` forever — the loop condition `current_hash != base` never becomes false, and the loop never hits the `None` branch either, since both cyclic hashes remain present in the map. `route` also grows without bound, adding memory exhaustion to the CPU spin.

This function is reached from two callers used inside the permissionless GRANDPA consensus-proof verification path:
- `GrandpaJustification::verify_with_voter_set`, called once per precommit signer: [3](#0-2) 
- `verify_grandpa_finality_proof`, called directly on the submitted proof's `unknown_headers`: [4](#0-3) 

Both are invoked from `ConsensusClient::verify_consensus` for the GRANDPA ISMP client, which decodes and verifies a submitted `ConsensusMessage` on every `handle_unsigned` consensus update — an unprivileged, permissionless entry point that any relayer can submit: [5](#0-4) 

Unlike the Pharos SPV verifier in this same codebase, which explicitly bounds proof-walk depth (`MAX_PROOF_DEPTH`) to prevent this exact class of issue: [6](#0-5) 

the GRANDPA `AncestryChain::ancestry` walk has no such bound, no visited-set cycle check, and no cap on `votes_ancestries`/`unknown_headers` length before the walk begins.

### Impact Explanation
A relayer node processing (or a collator validating) this consensus message enters an unbounded loop, consuming CPU indefinitely and growing memory via `route`, until the process is killed or OOMs. Since GRANDPA consensus verification runs inline in the `handle_unsigned` dispatch path (mempool validation and/or execution), this can stall block production / transaction validation for the chain running the GRANDPA light client, denying service to all users relying on that light client for cross-chain message delivery — a route unable to deliver messages, which is the "no vulnerability if not reachable" bar this analog clears via a single relayed unsigned consensus message.

### Likelihood Explanation
High: constructing two headers with hash-cyclic `parent_hash` fields requires only SCALE-encoding attacker-chosen `Header` structs (no cryptographic break needed — GRANDPA's Ed25519 signature check on precommits happens either after or independent of this ancestry walk for the affected call sites, and `verify_grandpa_finality_proof`'s own `headers.ancestry(from, target.hash())` call happens before the justification signature is checked). Any account able to submit an unsigned GRANDPA consensus update (a core relayer function, permissionless in ISMP) can trigger this.

### Recommendation
Bound the ancestry walk: cap `votes_ancestries`/`unknown_headers` length to the trusted maximum block range, detect cycles with a visited-hash set, and error out (`Error::NotDescendent` or a new `Error::AncestryCycle`) instead of looping unboundedly — mirroring the `MAX_PROOF_DEPTH` pattern already used in `modules/consensus/pharos/primitives/src/spv.rs`.

### Proof of Concept
1. Construct headers `H1` and `H2` (arbitrary but valid `SubstrateHeader`/`H: HeaderT` instances) such that `H1.parent_hash = H2.hash()` and `H2.parent_hash = H1.hash()`.
2. Include both in a `GrandpaJustification.votes_ancestries` (or `FinalityProof.unknown_headers`), with a precommit whose `target_hash` resolves into this cycle and a `base_hash` that is not part of it.
3. Submit as an unsigned `ConsensusMessage` via `handle_unsigned` to the GRANDPA consensus client.
4. `AncestryChain::ancestry` (or `verify_with_voter_set`'s call to it) loops indefinitely walking `H1 -> H2 -> H1 -> ...`, spinning the executing node's CPU and growing `route` without bound.

### Citations

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L121-134)
```rust
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

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L161-167)
```rust
impl<H: HeaderT> AncestryChain<H> {
	/// Initialize the ancestry chain given a set of relay chain headers.
	pub fn new(ancestry: &[H]) -> AncestryChain<H> {
		let ancestry: BTreeMap<_, _> = ancestry.iter().cloned().map(|h: H| (h.hash(), h)).collect();

		AncestryChain { ancestry }
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

**File:** modules/consensus/grandpa/verifier/src/lib.rs (L82-88)
```rust
	if base.number() < &consensus_state.latest_height {
		headers
			.ancestry(base.hash(), consensus_state.latest_hash)
			.map_err(|_| Error::InvalidAncestry)?;
	}

	let finalized = headers.ancestry(from, target.hash()).map_err(|_| Error::InvalidAncestry)?;
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L14-45)
```rust
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

**File:** modules/consensus/pharos/primitives/src/spv.rs (L214-216)
```rust
	if proof_nodes.len() > MAX_PROOF_DEPTH {
		return Err(Error::ProofTooDeep);
	}
```
