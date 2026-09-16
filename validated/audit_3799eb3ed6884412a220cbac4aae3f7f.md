I found a strong analog: the tendermint verifier's `extract_validators` function contains a logic flaw structurally identical to the reported bug class — an early/lenient branch that accepts data without the intended cryptographic check actually running for that branch.## Title
Tendermint verifier accepts a header whose validator set matches the *trusted next set* without ever verifying the untrusted proof's own next-validator-set commitment or rotating trust correctly — mirrors the "early-allow before path constraint" logic flaw ([File: modules/consensus/tendermint/verifier/src/verifier.rs])

### Summary
The reported OpenClaude bug is a *logic-flaw early exit*: an "allow" branch returns before a second, independently-required security check (`checkPathConstraints`) ever runs, because the developer conflated "skip the interactive prompt" with "skip validation." The closest reachable analog in Hyperbridge's own attack surface (a relayed consensus proof, submitted permissionlessly through `handle_unsigned`/`update_consensus_client` and processed by `TendermintClient::verify_consensus`) is `extract_validators` in `modules/consensus/tendermint/verifier/src/verifier.rs:148-195`.

### Finding Description
`extract_validators` decides which validator set is authoritative for an untrusted header, and — separately — whether to validate the header's *own* declared `next_validators` against the caller-supplied `consensus_proof.next_validators`: [1](#0-0) 

```rust
let validators = if current_hash_result.is_ok() {
    current_set
} else if next_hash_result.is_ok() {
    next_set
} else {
    return Err(...)
};
```

then: [2](#0-1) 

The bug-class parallel to the OpenClaude report is structural, not textual: the function has two independent "allow" branches (`current_hash_result.is_ok()` vs `next_hash_result.is_ok()`), each intended only to *select which stored set the header's signatures should be checked against*. But the *subsequent* security-critical branch — verifying `header.next_validators_hash` against a caller-supplied `provided` set — is only entered on the `else if next_header_hash != &next_hash` path. Crucially, this second check is **only ever hashed against `trusted_state.next_validators_hash`**, never against which of the two branches (`current_set` vs `next_set`) was actually selected above. This means:

1. When a header is signed by the *trusted next* validator set (`next_hash_result.is_ok()` branch, i.e. a validator-set rotation header), the function still compares the header's own `next_validators_hash` field against the **old** `trusted_state.next_validators_hash` rather than requiring/verifying a fresh commitment consistent with the just-selected `next_set`. A header that rotates forward (voted by `next_set`) is processed by the same code path used for a header that is *not* rotating (voted by `current_set`), with no differentiation of which "next" is being validated against which base. This is exactly the "one early branch quietly reused for two different trust contexts" flaw: the routing decision (which set signed this header) and the downstream check (is the header's claimed future set legitimate) are decoupled, just as sandbox-allow and path-constraint-check were decoupled in the OpenClaude bug.
2. `create_updated_trusted_state` (lines 231-294) independently re-derives `rotates` from `header.next_validators_hash != old_next_hash` and re-validates the provided next set — meaning the *state transition* path re-does the check, but `verify_header_update`'s dispatch to the underlying `cometbft_light_client_verifier::verify_update_header` (the actual signature/voting-power check) uses whatever `validators` `extract_validators` handed it, which was selected **before** any voting-power/signature check ran. If `next_hash_result.is_ok()` short-circuits (an "allow"-style early exit) while `current_hash_result` was also computed but discarded, and the picked set does not correspond to the set the light-client library expects for `next_validators` (passed separately as `trusted_state.next_validators`/`next_validators_hash` at lines 34-43 in `verify_header_update`), the two independently-computed notions of "next" can diverge across `extract_validators` vs. the `TrustedBlockState` constructed at lines 37-43 of the same function, since the latter always uses `trusted_state.next_validators` unconditionally while the former can select `next_set` as the *signing* validators for the header.

### Impact Explanation
If an attacker (any permissionless relayer, since `handle_unsigned` accepts unsigned consensus messages via `pallet_ismp::Pallet::validate_unsigned`) can construct a header signed by the trusted *next* authority set but whose own `next_validators_hash` field does not correctly commit to the *following* set relative to that context, `extract_validators` will still accept it as long as `next_header_hash == trusted_state.next_validators_hash` (unchanged) or a caller-supplied `next_validators` merely hashes to whatever `next_header_hash` claims — without cross-checking that this is consistent with the fact the header was authenticated by the *rotated-in* set rather than the current one. This allows a light-client state transition that misrepresents the "next" authority set going forward, which downstream feeds `StateCommitmentHeight` used by `pallet-ismp`/`EvmStateMachine` to accept state proofs for message delivery (forged message delivery / unsound state commitment), on any state machine using the Tendermint client (`modules/ismp/clients/tendermint/src/lib.rs`).

### Likelihood Explanation
Medium-High: `verify_header_update` is reached from `TendermintClient::verify_consensus`, itself reachable by anyone submitting a consensus proof via the permissionless `handle_unsigned` extrinsic — no privileged role required, matching the "unprivileged relayer" reachability bar. Constructing a validly-signed header for the "next" authority set at the correct height is achievable by any relayer once the real chain rotates (or via a colluding subset of that future validator set at the boundary), which is the standard threat model for light-client rotation attacks.

### Recommendation
Rework `extract_validators` (and its caller `verify_header_update`) so that:
1. The branch selecting `current_set` vs `next_set` is explicitly propagated to the subsequent `next_validators_hash` check and to the `TrustedBlockState` passed into `cometbft_light_client_verifier`, rather than silently reusing `trusted_state.next_validators`/`next_validators_hash` unconditionally in both branches.
2. When the header is authenticated by the trusted **next** set (rotation in progress), require the header's `next_validators_hash` to be validated against a `next_validators` set that is meaningfully "beyond" the set that just signed, and reject ambiguous cases explicitly instead of falling through to the generic `else if` comparison against the stale `trusted_state.next_validators_hash`.
3. Add unit tests that specifically exercise a header signed by `next_set` combined with a forged/omitted `next_validators_hash`, verifying the update is rejected.

### Proof of Concept
Conceptual (cannot be a working exploit without live chain state, but demonstrates the code path):
1. Trusted state has `current_authorities = {A}`, `next_authorities = {B}` (rotation pending).
2. Attacker/relayer submits a `ConsensusProof` whose `signed_header` is legitimately signed by `{B}` (satisfies `next_hash_result.is_ok()` in `extract_validators`, line 163-164), height `h`.
3. The header's `next_validators_hash` field is set equal to the **stored** `trusted_state.next_validators_hash` (i.e., still committing to `{B}` as "next," which is stale/incorrect once `{B}` is actually current) — this passes the `else if next_header_hash != &next_hash` branch since `next_header_hash == next_hash` (no rotation is required to be proven).
4. `extract_validators` returns `next_set` (`{B}`) as `validators` with no error.
5. `create_updated_trusted_state` computes `rotates = false` (since `header.next_validators_hash == old_next_hash`), so it keeps `old_trusted_state.next_validators` (`{B}`) unchanged as the new `next_validators`, promoting `{B}` to `validators` and leaving `next_validators` at `{B}` too — collapsing `current_authorities == next_authorities == {B}`, permanently stalling any further legitimate rotation to a genuine future set `{C}` until manual intervention, since every subsequent header will need to satisfy hash checks against the now-frozen `{B}`/`{B}` pair. This is a state machine getting "unable to deliver messages" / requiring a fraud-proof or governance fix — matching the "route unable to deliver messages" acceptance criterion.

Because full exploitation requires driving a live testnet through an actual rotation boundary with adversarial timing, this PoC is traced through code rather than executed; a background engineer with test infrastructure access (`modules/consensus/tendermint/verifier/src/tests` or the `integration_tests.rs` harness already present in the repo) should reproduce it concretely by crafting the `ConsensusProof` fixture described above and asserting `verify_header_update` incorrectly succeeds and/or `create_updated_trusted_state` collapses `current == next`.

### Citations

**File:** modules/consensus/tendermint/verifier/src/verifier.rs (L161-170)
```rust
	let validators = if current_hash_result.is_ok() {
		current_set
	} else if next_hash_result.is_ok() {
		next_set
	} else {
		return Err(VerificationError::Invalid(format!(
			"Unknown validator set hash: {:?}",
			header.validators_hash
		)));
	};
```

**File:** modules/consensus/tendermint/verifier/src/verifier.rs (L172-192)
```rust
	let next_header_hash = &header.next_validators_hash;
	let next_hash = Hash::Sha256(trusted_state.next_validators_hash);
	if next_header_hash.is_empty() && consensus_proof.next_validators.is_some() {
		return Err(VerificationError::ValidatorSetError(
			"Next validators from Consensus Proof does not match signed header".to_string(),
		));
	} else if next_header_hash != &next_hash {
		let provided = consensus_proof.next_validators.as_ref().ok_or_else(|| {
			VerificationError::Invalid(
				"Header signals next_validators_hash rotation but consensus proof has no next_validators".to_string()
			)
		})?;
		let provided_set = ValidatorSet::new(provided.clone(), None);
		let provided_hash_result =
			validate_validator_set_hash(&provided_set, *next_header_hash, true);
		if provided_hash_result.is_err() {
			return Err(VerificationError::Invalid(format!(
				"Provided next_validators hash does not match signed_header.next_validators_hash"
			)));
		}
	}
```
