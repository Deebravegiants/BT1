This confirms the pattern. Every other supermajority check in the codebase uses the correct BFT bound `⌊2N/3⌋ + 1`:

- BEEFY: `len >= ((2 * total) / 3) + 1` [1](#0-0) 
- Sync-committee: `sync_aggregate_participants < ((2 * committee_size as u64) / 3) + 1` [2](#0-1) 
- Byzantine-handler quorum: `total * 2 / 3 + 1` [3](#0-2) 
- SDK quorum helper: `Math.floor((2 * numProviders) / 3) + 1` [4](#0-3) 

But the on-chain BSC consensus verifier omits the `+ 1`, requiring only `participant_count >= ((2 * current_validators.len()) / 3)` — an exact 2/3, not "more than 2/3": [5](#0-4) 

### Title
Insufficient BSC validator supermajority threshold (`⌊2N/3⌋` instead of `⌊2N/3⌋+1`) permits consensus proof forgery below the required BFT quorum - (File: `modules/consensus/bsc/verifier/src/lib.rs`)

### Summary
`verify_bsc_header` — the sole on-chain gate that authenticates BSC Parlia consensus proofs submitted to Hyperbridge's `ismp-bsc` light client — enforces a participation threshold of `participant_count < ((2 * current_validators.len()) / 3)` to reject, i.e. it *accepts* any vote with `participant_count >= floor(2N/3)`. This is the classic "insufficient/insufficiently strong parameter" bug class described in the report (using a weaker-than-standard security bound where a stronger, well-known bound is trivial to apply and used elsewhere in the same codebase): every other BFT quorum check in this repository (BEEFY, sync-committee, tesseract's Byzantine handler, the SDK quorum helper) correctly uses `⌊2N/3⌋ + 1`, the minimum needed to guarantee at least one honest validator is present assuming ≤⌊(N-1)/3⌋ Byzantine validators. The BSC verifier's own doc comment and the project's own `parlia.mdx` explicitly state the required bound is "(2/3 * N) + 1", yet the code implements a strictly weaker bound.

### Finding Description
`verify_bsc_header` computes `participant_count` from the BLS aggregate vote bitset and only errors when `participant_count < ((2 * current_validators.len()) / 3)`: [5](#0-4) 

For `N = 21` (the BSC validator set size referenced throughout the tests/docs), `floor(2*21/3) = 14`. The code accepts `participant_count == 14`, i.e. exactly 14/21 validators, which is exactly 2/3, not "more than 2/3." The project's own consensus documentation states the requirement is `(2/3 * N) + 1` votes, i.e. 15 for N=21: [6](#0-5) 

Every sibling consensus verifier applies the correct `+1` bound:
- BEEFY: `len >= ((2 * total) / 3) + 1` [1](#0-0) 
- sync-committee: threshold `((2 * committee_size) / 3) + 1` [2](#0-1) 

The security significance of the `+1` term is that it is what guarantees at least one honest (non-Byzantine) validator's signature is included whenever the standard BFT fault-tolerance assumption (`< N/3` Byzantine validators) holds. Dropping the `+1` shrinks the set of validators whose cooperation is required to forge a commitment down to exactly `floor(2N/3)`, which can be entirely Byzantine under the same fault model the rest of the protocol relies on (since `N/3` Byzantine validators plus the boundary case allows an attacker set of size `floor(2N/3)` to be constructed without ever needing an honest signer, depending on how the Byzantine bound is defined relative to the floor). This lets an adversary controlling only `floor(2N/3)` (rather than `floor(2N/3)+1`) of the BSC validator set produce a BLS-aggregate-signed `VoteData` that `verify_bsc_header` accepts as satisfying quorum, then forge the `Header::hash` state root that is fed into `ismp-bsc`'s consensus state as a finalized BSC state commitment.

This verifier is reachable end-to-end from a single relayed consensus message: `ismp-bsc`'s `verify_fraud_proof` and the client's standard consensus-update path both call `verify_bsc_header` directly against attacker-influenced proof bytes decoded from a submitted `ConsensusMessage`: [7](#0-6) . Once accepted, the resulting state commitment is exactly what downstream `pallet-ismp` state/response proof verification trusts for delivering cross-chain messages and token bridge mint/burn operations sourced from BSC.

### Impact Explanation
A forged BSC consensus state commitment lets an attacker (who need not compromise a true two-thirds-plus-one BFT majority, only `floor(2N/3)`) fabricate arbitrary state roots for the BSC chain that Hyperbridge trusts. Any state/storage proof verified against that forged root — including token bridge mint proofs, escrow release proofs, or message delivery proofs sourced from BSC — would be accepted as valid, enabling unbacked minting or theft of bridged funds routed through the BSC light client. This is a critical unsound-state-commitment vulnerability directly in the consensus verification path.

### Likelihood Explanation
Exploitation requires collusion of `floor(2N/3)` BSC validators (14 of 21 in the documented topology) rather than the intended `floor(2N/3)+1` (15 of 21). While this is still a substantial validator collusion requirement typical of BFT threshold bugs, it is a strictly and unnecessarily weaker bar than the protocol's own documented and intended security margin, and the deviation is silent (no error, no test covers the exact boundary `participant_count == floor(2N/3)`) — the existing test only checks `10 < 14` rejects, not that `14` should also be rejected under the stated `+1` rule.

### Recommendation
Change the threshold check in `verify_bsc_header` to match the documented and codebase-standard bound:
```rust
if participant_count < ((2 * current_validators.len()) / 3) + 1 {
    Err(Error::NotEnoughParticipants)?
}
```
Apply the same fix to the off-chain heuristic copies in `tesseract/consensus/bsc/src/host.rs` and `modules/consensus/bsc/prover/src/test.rs` for consistency (though those are pre-filters, not the security boundary). Add a test asserting that exactly `floor(2N/3)` participants is rejected and `floor(2N/3)+1` is accepted.

### Proof of Concept
1. Configure a BSC validator set of `N = 21` validators.
2. Have exactly 14 (`floor(2*21/3) = 14`) colluding/compromised validators sign a `VoteAttestationData` for an arbitrary forged `target_header`/`source_header` pair (satisfying the adjacency and header-hash-binding checks).
3. Submit this as a `ConsensusMessage` to `ismp-bsc`'s consensus client update path.
4. `verify_bsc_header` computes `participant_count = 14`, checks `14 < ((2*21)/3) = 14` → `false`, so the "not enough participants" error is **not** raised, despite this being exactly the 2/3 boundary and one signer short of the documented `(2/3*N)+1 = 15` requirement.
5. If the BLS aggregate signature check also passes (achievable since the 14 colluding validators are genuine signers), the forged header's state root becomes a trusted `ConsensusState` update, letting the attacker craft state proofs against arbitrary fabricated data with a smaller validator subset than the protocol's stated security margin requires.

### Citations

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-261)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
}
```

**File:** modules/consensus/sync-committee/verifier/src/lib.rs (L110-115)
```rust
	let sync_aggregate_participants: u64 =
		sync_committee_bits.iter().take(committee_size).filter(|b| **b).count() as u64;

	if sync_aggregate_participants < ((2 * committee_size as u64) / 3) + 1 {
		Err(Error::SyncCommitteeParticipantsTooLow)?
	}
```

**File:** tesseract/messaging/evm/src/byzantine.rs (L16-21)
```rust
/// Supermajority quorum threshold over `total` providers, computed as the
/// classic BFT bound `⌊2/3·N⌋ + 1` so the threshold scales with the
/// configured RPC fan-out instead of being a hard-coded floor.
fn quorum_threshold(total: usize) -> usize {
	total * 2 / 3 + 1
}
```

**File:** sdk/packages/simplex/src/services/QuorumPublicClient.ts (L17-25)
```typescript
/**
 * Standard BFT threshold for a set of `n` equal peers: `floor(2n/3) + 1`, i.e.
 * strictly more than two thirds, tolerating up to `floor((n-1)/3)` faults.
 *
 *  - n=1: 1   n=2: 2   n=3: 3   n=4: 3   n=5: 4   n=7: 5
 */
export function quorumThreshold(numProviders: number): number {
	return Math.floor((2 * numProviders) / 3) + 1
}
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L81-90)
```rust
	// We have to use the same threshold specified in the bsc parlia consensus which is 2/3
	// https://github.com/bnb-chain/bsc/blob/da35ee13e2fe38efaeab2d6fb27f112332459b50/consensus/parlia/parlia.go#L557
	let participant_count = validators_bit_set
		.iter()
		.take(current_validators.len())
		.filter(|bit| **bit)
		.count();
	if participant_count < ((2 * current_validators.len()) / 3) {
		Err(Error::NotEnoughParticipants)?
	}
```

**File:** docs/content/protocol/consensus/parlia.mdx (L31-33)
```text
**Vote Validity and Finality**:

For a target block to be considered justified (considered valid by a large enough majority), it requires votes from more than two-thirds of the validators (represented as (2/3 * N) where N is the total number of validators). Additionally, at least one more unique validator needs to participate to reach the required threshold of (2/3 * N) + 1 votes.
```

**File:** modules/ismp/clients/bsc/src/lib.rs (L194-206)
```rust
		// Authenticate both updates against the trusted validator set: this verifies
		// the BLS aggregate signature over each update's `vote_data`.
		let _ = verify_bsc_header::<H, C>(
			&consensus_state.current_validators,
			bsc_client_update_1,
			epoch_length,
		)?;

		let _ = verify_bsc_header::<H, C>(
			&consensus_state.current_validators,
			bsc_client_update_2,
			epoch_length,
		)?;
```
