## Finding: Off-by-one quorum check in BSC consensus verifier allows finalization with less than the required supermajority

### Title
Missing `+1` in BSC light client supermajority threshold permits state-commitment finalization one vote below the fast-finality quorum - (File: `modules/consensus/bsc/verifier/src/lib.rs`)

### Summary
The reported bug class is a miscounting/off-by-one error in a vote-tallying comparison that silently weakens a quorum requirement, letting a result that should be rejected pass as valid. The same class of bug exists in Hyperbridge's BSC (`Parlia`) consensus verifier: the supermajority check accepts a validator set participation count that is exactly one vote short of the BFT threshold documented and used elsewhere in the codebase.

### Finding Description
`verify_bsc_header` in [1](#0-0)  computes `participant_count` from the vote bit-set and rejects only when:

```rust
if participant_count < ((2 * current_validators.len()) / 3) {
    Err(Error::NotEnoughParticipants)?
}
```

This means an update is accepted whenever `participant_count >= floor(2N/3)`, i.e. it lacks the `+ 1` term. Every other supermajority/quorum computation in this same repository requires strictly more than 2/3, i.e. `>= (2N/3) + 1`:

- BEEFY (Rust): `len >= ((2 * total) / 3) + 1` at [2](#0-1) 
- BEEFY (Solidity): `return len >= ((2 * total) / 3) + 1;` at [3](#0-2) 
- Ethereum sync-committee: `if sync_aggregate_participants < ((2 * committee_size as u64) / 3) + 1` at [4](#0-3) 
- Pharos: `let required = (total_stake * 2 / 3) + 1;` at [5](#0-4) 

The project's own consensus documentation for Parlia/BSC also states the correct requirement explicitly: finalization requires votes from *more than* two-thirds of validators, "at least one more unique validator needs to participate to reach the required threshold of `(2/3 * N) + 1` votes" — see [6](#0-5) .

The BSC verifier's inline comment claims parity with upstream `bnb-chain/bsc` parlia logic, but the implemented comparison omits the `+1` that both the documentation and every sibling consensus client in this repo implement. As a direct consequence:
- For any `N` where `2N` is exactly divisible by `3` (e.g. `N = 21`, the BSC mainnet/testnet validator-set size referenced in the module's own tests, see [7](#0-6) ), `floor(2N/3) = 14`, and the check accepts exactly `14` signers — precisely the boundary that the documented rule (`(2/3*N)+1 = 15`) says must be rejected.
- For `N` not divisible by 3, integer truncation additionally rounds `2N/3` down, compounding the shortfall.

### Impact Explanation
This check gates acceptance of a BSC/Parlia consensus update used to finalize `source_header`'s state root as a trusted BSC state commitment within Hyperbridge's ISMP BSC light client (`verify_bsc_header` return value feeds into finalized-header/state-commitment updates consumed by relayers/handlers). Accepting an update with one fewer validator signature than the actual BFT quorum means a coalition that does not hold true supermajority stake/voting power (e.g. colluding minority validators plus the fast-finality mechanics of BSC) can get a state commitment finalized by the light client that would not be considered final by the real BSC network. This is a consensus-soundness break for the BSC route: it can enable forged/incorrect state commitments to be delivered and trusted, which downstream can be leveraged for unauthorized message delivery or state proofs against fabricated finalized headers — a direct "unsound state commitment / forged message delivery" outcome for BSC-routed messages.

### Likelihood Explanation
The vulnerable comparison executes on every single BSC consensus update submitted by any relayer — there is no privileged actor requirement to trigger it; a normal, permissionless relayer submission that happens to carry the boundary participant count (very plausible given BSC's fixed 21-validator epoch set, where the boundary count of 14 is a completely ordinary, easily reachable multi-validator quorum) will be accepted where it should be rejected. No other check downstream re-validates that the true supermajority threshold with `+1` was met.

### Recommendation
Change the check to match the documented Parlia rule and the rest of the codebase's convention:
```rust
if participant_count < ((2 * current_validators.len()) / 3) + 1 {
    Err(Error::NotEnoughParticipants)?
}
```
Add a test mirroring `rejects_too_few_in_range_participants` that specifically asserts `participant_count == floor(2N/3)` (e.g., 14 of 21) is rejected, not just `< floor(2N/3)`.

### Proof of Concept
1. Construct a `BscClientUpdate` for a 21-validator epoch (as in the existing test helper `dummy_validators(21)` at [8](#0-7) ).
2. Set exactly 14 in-range bits in `vote_address_set` (mask `(1u64 << 14) - 1`), leaving all bits `[14,21)` clear so only 14 of 21 validators are marked as participants.
3. Call `verify_bsc_header`; the current check `participant_count < (2*21)/3 = 14` evaluates `14 < 14 == false`, so the `NotEnoughParticipants` error is *not* raised, and the update proceeds to signature/finalization processing — despite 14/21 being exactly the two-thirds boundary that the protocol's own spec (and the code's sibling BEEFY/sync-committee/Pharos checks) require to be exceeded by at least one additional signer.

### Citations

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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-261)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
}
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L240-243)
```text
    // @dev Check for supermajority participation.
    function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
        return len >= ((2 * total) / 3) + 1;
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

**File:** modules/consensus/pharos/verifier/src/lib.rs (L163-167)
```rust
) -> Result<(), Error> {
	let participating_stake = validator_set.participating_stake(participants);
	let total_stake = validator_set.total_stake;
	let required = (total_stake * 2 / 3) + 1;

```

**File:** docs/content/protocol/consensus/parlia.mdx (L31-37)
```text
**Vote Validity and Finality**:

For a target block to be considered justified (considered valid by a large enough majority), it requires votes from more than two-thirds of the validators (represented as (2/3 * N) where N is the total number of validators). Additionally, at least one more unique validator needs to participate to reach the required threshold of (2/3 * N) + 1 votes.

**Finalizing the Source Block**:

When a target block receives sufficient justification votes, the corresponding source block (the reference point) is considered finalized.
```
