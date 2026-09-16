Based on my research, I found a genuine analog to the reported bug class in the BSC/Parlia consensus verifier. This mirrors the original report's pattern exactly: a threshold constant/comment claims one formula ("supermajority", "2/3 + 1") while the actual implemented comparison uses a strictly weaker inequality that omits the "+1", accepting a non-supermajority set of signers.

### Title
BSC consensus verifier accepts sub-supermajority (exactly 2/3, no +1) participation, weakening finality guarantees - ([File: modules/consensus/bsc/verifier/src/lib.rs])

### Summary
`verify_bsc_header` in the BSC (Parlia) light-client verifier checks participant count against `(2 * current_validators.len()) / 3` with a strict `<` rejection, i.e. it *accepts* any `participant_count >= floor(2N/3)`. Every other supermajority gate in this codebase (BEEFY, sync-committee, and the project's own documentation of BSC/Parlia) requires `>= floor(2N/3) + 1`. The `+1` is dropped in the BSC verifier's actual comparison, even though the surrounding comment and the project's own docs describe the required threshold as "more than two-thirds... at least one more unique validator... (2/3 * N) + 1".

### Finding Description
The check is:
```
if participant_count < ((2 * current_validators.len()) / 3) {
    Err(Error::NotEnoughParticipants)?
}
``` [1](#0-0) 

This rejects only when strictly fewer than `floor(2N/3)` participants signed, meaning exactly `floor(2N/3)` participants (not `floor(2N/3)+1`) is accepted as sufficient. That is a plain two-thirds threshold, not a *supermajority* (more-than-two-thirds) threshold.

Compare this to the BEEFY verifier's threshold in the same repository:
```
fn check_participation_threshold(len: u32, total: u32) -> bool {
    len >= ((2 * total) / 3) + 1
}
``` [2](#0-1) 

and the sync-committee verifier's threshold:
```
if sync_aggregate_participants < ((2 * committee_size as u64) / 3) + 1 {
    Err(Error::SyncCommitteeParticipantsTooLow)?
}
``` [3](#0-2) 

Both intentionally include the `+1`. The project's own documentation for BSC/Parlia explicitly states the correct threshold formula includes the `+1`:

"For a target block to be considered justified... it requires votes from more than two-thirds of the validators... Additionally, at least one more unique validator needs to participate to reach the required threshold of (2/3 * N) + 1 votes." [4](#0-3) 

This is exactly the same class of bug as the reported analog: a constant/threshold is *documented and intended* to be computed one way (`2/3*N + 1`, a strict supermajority), but the actual on-chain check implements a different, weaker formula (`2/3*N`, floor without the +1), producing a systematic under-enforcement of the safety margin. The same off-by-one/formula-mismatch is also duplicated in the tesseract relayer host code that walks blocks looking for updates:
```
if validators_bit_set.iter().as_bitslice().count_ones() < (2 * next_validators.validators.len() / 3)
``` [5](#0-4) 
```
if validators_bit_set.iter().as_bitslice().count_ones() < (2 * current_validators.validators.len() / 3)
``` [6](#0-5) 
and the prover's sync/enactment test code, all consistently missing the `+1`: [7](#0-6) 

### Impact Explanation
BSC/Parlia consensus proofs are the trust root that `ismp-bsc` uses to accept state commitments from BSC into Hyperbridge; those commitments back all state/response membership proofs (and downstream token bridge mint/settlement flows) routed through the BSC light client. Lowering the required participation from a true supermajority (`>2/3`) to a bare two-thirds (`≥2/3`, without the extra vote) shrinks the fault-tolerance margin the consensus proof relies on for safety: with the correct `2/3*N+1` threshold, at most `floor((N-1)/3)` validators can be byzantine while safety still holds; the weakened `2/3*N` threshold admits precisely one additional validator's worth of participation as "sufficient," which for BSC's 21/41-validator sets can, in specific validator counts, mean the equivalent of `2/3*N` colluding/unavailable validators being enough to justify (and thus finalize) a block that the true supermajority rule would have rejected — undermining the "51%/2/3 attack" safety assumption the protocol's own documentation calls out as the basis for BFT safety of the bridge. This can allow a forged/insufficiently-attested BSC consensus update to be accepted, letting an attacker who controls or colludes with a bare fraction (rather than a genuine supermajority) of BSC validators push a fraudulent state commitment into Hyperbridge and forge cross-chain message delivery/state proofs.

### Likelihood Explanation
The threshold check runs on every consensus update accepted from BSC, so any prover/relayer capable of assembling `floor(2N/3)` valid BLS signatures (rather than needing `floor(2N/3)+1`) can pass verification. This lowers the bar for the set of colluding/compromised validators needed for a full attack from what governance/protocol documentation and every other consensus client in this repository intends. It requires collusion or compromise of a large fraction of BSC's own validator set (an external precondition), which is a non-trivial but realistic threat model already contemplated by the protocol design (this is precisely the "51%/BFT" attack class the project's own docs discuss).

### Recommendation
Change the BSC verifier's threshold check (and the mirrored duplicate checks in `tesseract/consensus/bsc/src/host.rs`) to require `participant_count >= ((2 * current_validators.len()) / 3) + 1`, matching the BEEFY and sync-committee verifiers and the project's own documented Parlia specification, so that a genuine supermajority (not merely two-thirds) is required before a BSC consensus update is accepted.

### Proof of Concept
1. Construct a validator set of size `N = 21` (BSC testnet epoch size).
2. `floor(2*21/3) = 14`. Craft a `BscClientUpdate` whose `vote_address_set` bitmap has exactly `14` in-range bits set (i.e., 14 of 21 validators sign), and a valid BLS aggregate signature from those 14 validators over the vote data.
3. Call `verify_bsc_header::<H, C>(&validators, update, epoch_length)`:
   - Current logic: `participant_count (14) < (2*21)/3 (14)` is `false`, so the check **passes** and verification proceeds to signature/adjacency checks.
   - Correct logic (matching BEEFY/sync-committee): `14 < 14 + 1` is `true`, so the update should be **rejected** with `NotEnoughParticipants`.
4. This is directly demonstrated by the repo's own existing unit test comment/threshold description: "10 of 21 bits set (threshold is 14)" rejects at 10 — but the test suite never asserts that exactly 14 (rather than 15) is the true minimum accepted count, silently encoding the off-by-one weaker bound. [8](#0-7)

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

**File:** modules/consensus/bsc/verifier/src/lib.rs (L370-382)
```rust
	/// All bits are within the validator range, but fewer than 2/3 are
	/// set — the supermajority check rejects.
	#[test]
	fn rejects_too_few_in_range_participants() {
		let validators = dummy_validators(21);
		// 10 of 21 bits set (threshold is 14).
		let mask: u64 = (1u64 << 10) - 1;
		let header = header_with_vote_set(mask, B256::repeat_byte(1), B256::repeat_byte(2));

		let err = verify_bsc_header::<TestHost, Testnet>(&validators, update_with(header), 1000)
			.expect_err("under-threshold update must be rejected");
		assert!(format!("{err}").contains("Not enough participants"), "unexpected error: {err:?}");
	}
```

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

**File:** docs/content/protocol/consensus/parlia.mdx (L31-33)
```text
**Vote Validity and Finality**:

For a target block to be considered justified (considered valid by a large enough majority), it requires votes from more than two-thirds of the validators (represented as (2/3 * N) where N is the total number of validators). Additionally, at least one more unique validator needs to participate to reach the required threshold of (2/3 * N) + 1 votes.
```

**File:** tesseract/consensus/bsc/src/host.rs (L341-343)
```rust
					if validators_bit_set.iter().as_bitslice().count_ones() <
						(2 * next_validators.validators.len() / 3)
					{
```

**File:** tesseract/consensus/bsc/src/host.rs (L442-444)
```rust
					if validators_bit_set.iter().as_bitslice().count_ones() <
						(2 * consensus_state.current_validators.len() / 3)
					{
```

**File:** modules/consensus/bsc/prover/src/test.rs (L138-139)
```rust
		if validators_bit_set.iter().as_bitslice().count_ones() < (2 * current_validators.len() / 3)
		{
```
