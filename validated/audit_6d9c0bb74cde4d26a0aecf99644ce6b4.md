### Title
BSC consensus verifier's integer-truncated supermajority threshold accepts zero signers when the validator set shrinks to size ≤ 1 - ([File: modules/consensus/bsc/verifier/src/lib.rs])

### Summary
`verify_bsc_header` computes the required BEP-126 supermajority as `(2 * current_validators.len()) / 3` using integer (floor) division and only rejects when `participant_count < required`. When `current_validators.len()` is `0` or `1`, this expression truncates to `0`, so the inequality `participant_count < 0` can never be true — the "supermajority" check silently passes even with **zero** participating validators. Nothing elsewhere in the validator-set-extraction path prevents `current_validators` from reaching size `1`, because the guard that gates staging a new validator set only rejects an **empty** list (`!validators.is_empty()`), not a degenerate one-validator list. This mirrors the reported bug class: an empty (or effectively-empty) authorization/approver set is treated as automatically satisfying the check that is supposed to gate the action.

### Finding Description
In `modules/consensus/bsc/verifier/src/lib.rs`, the participation gate is: [1](#0-0) 

```
if participant_count < ((2 * current_validators.len()) / 3) {
    Err(Error::NotEnoughParticipants)?
}
```

With `current_validators.len() == 1`, `(2*1)/3 == 0` (Rust integer division floors), so the condition becomes `participant_count < 0`, which is always false for an unsigned/`usize` count — the check is a no-op and the proof proceeds with `participant_count == 0`.

The set of "participants" is derived purely from the caller-supplied `vote_address_set` bitmap zipped against `current_validators`: [2](#0-1) 

If no bits are set, `participants` is empty. `aggregate_public_keys(&[])` starts from the BLS12-381 identity point and folds over zero keys, returning the identity/point-at-infinity public key: [3](#0-2) 

A BLS pairing check against an identity public key is satisfied only by the identity signature (`e(O, H(m)) = 1 = e(g1, σ) ⇔ σ = O`), which is a fixed, publicly-known encoding (the BLS12-381 "infinity" compressed point), not a forged real signature. `bls::verify` is called with this attacker-supplied, zero-participant aggregate and no explicit `participants.is_empty()` guard exists in this verifier (contrast with the Pharos verifier, which explicitly checks `if participants.is_empty() { return Err(Error::NoParticipants) }` before calling `verify`): [4](#0-3) [5](#0-4) 

Crucially, nothing prevents `current_validators` from legitimately reaching size `1`. The only guard on newly-extracted validator sets (staged as `next_validators`, later promoted to `current_validators` on rotation) rejects only an **empty** list: [6](#0-5) [7](#0-6) 

A validator set with exactly one entry passes `!validators.is_empty()` and is happily staged/promoted, after which the threshold degenerates as described.

### Impact Explanation
Once `current_validators.len()` is `0` or `1` for a BSC light client tracked by Hyperbridge, any unprivileged relayer can submit a `BscClientUpdate` with an all-zero `vote_address_set` (zero participants) and the fixed identity-point BLS signature. The verifier accepts this as a validly finalized `(source_header, target_header)` pair as long as the RLP-encoded headers satisfy the adjacency/hash checks the attacker fully controls (they are not required to be real BSC chain data — only internally consistent). This forges consensus updates for the BSC state machine, letting the attacker commit an arbitrary state root, which downstream can be used to forge state/membership proofs for message delivery, minting, or other app-level actions gated on that light client — a forged-message-delivery / unsound-state-commitment class impact.

### Likelihood Explanation
The precondition (`current_validators.len() ∈ {0,1}`) is not the current expected state of a live BSC validator set (production BSC has dozens of validators), so this is not exploitable against a healthy, correctly-initialized mainnet client. It becomes reachable only if the trusted validator set is ever driven down to size ≤ 1 — e.g., through misconfiguration, a non-mainnet/test deployment of the client, or any future epoch-header path that could legitimately encode a single validator. The code itself provides no defense-in-depth (no minimum-set-size check, no explicit "reject empty/degenerate participant set" as done in the sibling Pharos verifier), so it is a latent authorization-bypass bug rather than a directly-triggerable-today exploit under normal mainnet parameters. Given the uncertainty about whether any operational path (e.g., testnet configuration, chain with fewer validators) can plausibly reach `len() == 1`, this should be treated as Medium likelihood.

### Recommendation
- Use a strict majority formula that cannot truncate to zero, e.g. require `participant_count * 3 > 2 * current_validators.len()` (or equivalently `participant_count >= (2*len + 2)/3` using ceiling division), matching the same fix pattern already used correctly elsewhere.
- Add an explicit `if participants.is_empty() { return Err(Error::NoParticipants) }` guard before calling `aggregate_public_keys`/`bls::verify`, exactly as done in the Pharos verifier (`modules/consensus/pharos/verifier/src/lib.rs`), so a zero-participant proof can never reach the pairing check regardless of `current_validators.len()`.
- Enforce a sane minimum validator-set size (e.g. `> 1`, ideally matching BEP-126's realistic minimum) when staging `next_validators`, instead of only rejecting the empty case.

### Proof of Concept
1. Bring a BSC light client (via `ismp-bsc`) to a state where `current_validators.len() == 1` (e.g., a test/staging deployment or a hypothetical epoch header that legitimately encodes one validator, which passes today's `!validators.is_empty()` guard).
2. Craft a `BscClientUpdate` where:
   - `extra_data.vote_address_set` has all bits `0` (no participants).
   - `extra_data.agg_signature` is the fixed BLS12-381 G2 identity/point-at-infinity encoding.
   - `source_header`/`target_header` are attacker-constructed headers satisfying `vote_data.source_hash`/`target_hash` equality and the direct-child adjacency check.
3. Submit via `verify_bsc_header`. `participant_count = 0`, `((2*1)/3) = 0`, so `0 < 0` is false — `NotEnoughParticipants` is never raised. `aggregate_public_keys(&[])` yields the identity key; `bls::verify` against the identity key and the identity signature returns `true`. The forged update is accepted as finalized BSC state.

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

**File:** modules/consensus/bsc/verifier/src/lib.rs (L174-183)
```rust

            if !validators.is_empty() {
                Some(NextValidators {
                    validators,
                    rotation_block: epoch_header.number.low_u64() +
                        (current_validators.len() as u64 / 2),
                })
            } else {
                Err(Error::MissingValidatorSet)?
            }
```

**File:** modules/consensus/bsc/verifier/src/lib.rs (L185-202)
```rust
        } else if update.source_header.number.low_u64() % epoch_length == 0 {
            let epoch_header_extra_data = parse_extra::<H, C>(&update.source_header)
                .map_err(|_| Error::ParseEpochExtraData)?;
            let validators = epoch_header_extra_data
                .validators
                .into_iter()
                .map(|val| val.bls_public_key.as_slice().try_into().expect("Infallible"))
                .collect::<Vec<BlsPublicKey>>();

            if !validators.is_empty() {
                Some(NextValidators {
                    validators,
                    rotation_block: update.source_header.number.low_u64() +
                        (current_validators.len() as u64 / 2),
                })
            } else {
                Err(Error::MissingValidatorSet)?
            }
```

**File:** modules/utils/bls-utils/src/bls.rs (L46-52)
```rust
pub fn aggregate_public_keys(keys: &[BlsPublicKey]) -> Result<Vec<u8>, BLSError> {
	let mut aggregate = G1ProjectivePoint::default();
	for key in keys {
		aggregate = aggregate + pubkey_to_projective(key)?;
	}
	Ok(bls::point_to_pubkey(aggregate.into()))
}
```

**File:** modules/consensus/pharos/verifier/src/lib.rs (L179-188)
```rust
/// Verify the BLS aggregate signature.
fn verify_bls_signature(
	participants: &[BlsPublicKey],
	block_proof: &BlockProof,
	block_proof_hash: H256,
) -> Result<(), Error> {
	if participants.is_empty() {
		return Err(Error::NoParticipants);
	}

```
