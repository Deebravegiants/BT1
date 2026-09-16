### Title
BSC Parlia consensus verifier's supermajority threshold rounds down to zero (or below the real 2/3 bound) for small validator sets - (File: modules/consensus/bsc/verifier/src/lib.rs)

### Summary
`verify_bsc_header` gates acceptance of a BSC/Parlia header finalization on a supermajority participation check that uses integer division without a `+1` correction term, unlike every other quorum/threshold check in the codebase. For small validator-set sizes this integer-division truncation collapses the required threshold to zero or to a value below the genuine 2/3 bound, exactly mirroring the Nouns-Builder `quorum()` bug where `totalSupply * bps / 10_000` rounds to zero and the gate becomes a no-op.

### Finding Description
The participation check is: [1](#0-0) 

```rust
if participant_count < ((2 * current_validators.len()) / 3) {
    Err(Error::NotEnoughParticipants)?
}
```

For `current_validators.len() == 1`, `(2*1)/3 = 0` (integer division), so the condition `participant_count < 0` is always false for an unsigned integer — a header with **zero** signing validators passes the participation gate. For `len() == 2`, the required threshold is `(2*2)/3 = 1`, i.e. only 50% of the validator set is required instead of a genuine 2/3 supermajority.

Every other supermajority check in the same codebase adds the missing `+1` term to avoid exactly this truncation hazard: [2](#0-1) [3](#0-2) [4](#0-3) 

The BSC/Parlia check is the sole outlier that omits it, even though the accompanying comment states it is meant to mirror "the same threshold specified in the bsc parlia consensus," which is `signersCount < (2*len(validators))/3`. Carrying that exact (already-truncating) formula into an on-chain light client used to gate cross-chain state commitments reproduces the same rounding-to-zero defect described in the report: the effective quorum silently degrades to nothing for small validator-set sizes, and the check that is supposed to reject under-participation becomes a no-op.

### Impact Explanation
This check gates `verify_bsc_header`, which is the sole authority-participation guard before the code proceeds to reconstruct an aggregate BLS public key only from the bits actually marked in `validators_bit_set` and verifies the signature against it: [5](#0-4) 

If the effective validator set the client is tracking is ever small (e.g. a BSC-compatible/Parlia-based chain configured or bootstrapped with a small validator committee, or a validator set that has shrunk), the participation gate can be satisfied by far fewer signers than the intended 2/3 supermajority — down to zero signers when `len()==1`. Any relayer submitting `BscClientUpdate` through `verify_bsc_header` is otherwise unprivileged. A forged/under-signed consensus update accepted here directly translates into an unsound state commitment being finalized for the tracked state machine, which downstream ISMP consumers (state/non-membership proofs, token bridge mint/burn, message delivery) treat as canonical — i.e. forged message delivery / unsound state commitment risk.

### Likelihood Explanation
On BSC mainnet itself the validator set is always ~21–41, so this exact truncation (`len ∈ {1,2}`) is not reachable in that specific deployment. However, this verifier is generic Parlia-consensus code (`Config` is chain-parameterized, tests exercise `Testnet`), intended to be reused for any Parlia/BSC-fork chain the protocol chooses to support, and the check is a straightforward, unconditional integer-division bug independent of any specific chain's validator count — it degrades progressively (not just at the extreme `len==1` case, `len==2` already only requires 50% instead of 67%). This is a genuine code-level defect reachable by any relayer submitting a consensus proof to this verifier, on any deployment with a modest validator set size, matching the report's root cause and judged severity band (Medium).

### Recommendation
Add the missing `+1` (or otherwise use a non-truncating supermajority comparison, e.g. `3 * participant_count > 2 * current_validators.len()` or `participant_count * 3 >= current_validators.len() * 2 + 1`) so the threshold can never round down to a trivially satisfiable value, consistent with the `beefy`, `sync-committee`, and `pharos` verifiers in this same codebase:

```rust
if participant_count < ((2 * current_validators.len()) / 3) + 1 {
    Err(Error::NotEnoughParticipants)?
}
```

### Proof of Concept
1. Construct (or configure) a `TendermintClient`-style BSC/Parlia light client instance where `current_validators.len() == 1` (a single-validator Parlia-based chain, or any deployment reduced to 1–2 validators).
2. Craft a `BscClientUpdate` whose `attested_header.extra_data` encodes a `VoteAttestationData` with `vote_address_set = 0` (no bits set) and an arbitrary/invalid `agg_signature`.
3. Call `verify_bsc_header::<H, C>(&current_validators, update, epoch_length)`.
4. With `current_validators.len() == 1`, `participant_count = 0` and the threshold `((2*1)/3) = 0`; the condition `0 < 0` is false, so the `NotEnoughParticipants` gate is bypassed even though zero validators actually signed — as shown by the existing test structure at: [6](#0-5) 
which only exercises the check at `len=21`, never validating behavior at small validator-set sizes where the rounding defect manifests.

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

**File:** modules/consensus/bsc/verifier/src/lib.rs (L113-133)
```rust
	let participants: Vec<BlsPublicKey> = current_validators
		.iter()
		.zip(validators_bit_set.iter())
		.filter_map(|(validator, bit)| if *bit { Some(validator.clone()) } else { None })
		.collect();

	let aggregate_public_key = aggregate_public_keys(&participants)
		.map_err(|err| Error::AggregatePublicKeys(alloc::format!("{err:?}")))?;
	let msg = H::keccak256(alloy_rlp::encode(extra_data.vote_data.clone()).as_slice());
	let signature = extra_data.agg_signature;

	let verify = bls::verify(
		&aggregate_public_key,
		&msg.as_ref().to_vec(),
		signature.to_vec().as_ref(),
		&bls::DST_ETHEREUM.as_bytes().to_vec(),
	);

	if !verify {
		Err(Error::InvalidSignature)?
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

**File:** modules/consensus/pharos/verifier/src/lib.rs (L159-177)
```rust
/// Verify that participating validators have more than 2/3 of total stake.
fn verify_stake_threshold(
	validator_set: &ValidatorSet,
	participants: &[BlsPublicKey],
) -> Result<(), Error> {
	let participating_stake = validator_set.participating_stake(participants);
	let total_stake = validator_set.total_stake;
	let required = (total_stake * 2 / 3) + 1;

	if participating_stake >= required {
		Ok(())
	} else {
		Err(Error::InsufficientStake {
			participating: participating_stake,
			required,
			total: total_stake,
		})
	}
}
```
