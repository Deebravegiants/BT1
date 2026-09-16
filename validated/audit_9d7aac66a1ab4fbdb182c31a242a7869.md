### Title
Off-by-one in `verify_delay_passed` blocks message delivery exactly at the challenge-period boundary - ([File: modules/ismp/core/src/handlers.rs])

### Summary
`verify_delay_passed` in the core ISMP handler uses a strict `>` comparison to decide whether a state machine's configured challenge period has elapsed, while the EVM `HandlerV2` equivalent uses an inclusive `>=` comparison for the same check. This mirrors the reported bug class exactly (`<` used where `<=`/inclusive boundary is required), but on the pallet-ismp side the reachable analog only produces a bounded one-block/one-timestamp delay rather than fund loss.

### Finding Description
`verify_delay_passed` gates every incoming request, response, and timeout message processed by `pallet-ismp` against a configured `challenge_period` for the source state machine: [1](#0-0) 

The check only returns `true` (challenge period elapsed, message may proceed) when `current_timestamp - update_time > delay_period`, i.e., strictly greater than the configured period. At the exact boundary, where `current_timestamp - update_time == delay_period`, the function returns `false` and `validate_state_machine` rejects the message with `ChallengePeriodNotElapsed`: [2](#0-1) 

This is inconsistent with the equivalent EVM logic in `HandlerV2`, which treats the boundary as elapsed (inclusive): [3](#0-2) 

There, `challengePeriod > delay` reverts, so `delay == challengePeriod` is accepted — the opposite (correct) boundary treatment of the same invariant. The Rust core client is stricter and rejects that same instant, exactly matching the off-by-one class described in the external report (`<` instead of `<=`, denying an action that is legitimately within the allowed window).

### Impact Explanation
A relayer or dispatcher attempting to deliver a request, response, or timeout proof at the exact instant the challenge period elapses (down to the timestamp granularity of the host) will have their submission rejected with `ChallengePeriodNotElapsed`, even though the period has technically elapsed per the intended semantics used on the EVM side. The relayer must wait for the clock to advance by at least one more unit and resubmit. This does not cause theft, permanent freezing of funds, or unsound state commitments — it is a bounded, self-resolving delay of at most one timestamp increment, after which the identical message succeeds on resubmission.

### Likelihood Explanation
Hitting the exact boundary timestamp requires submitting in the same instant the challenge period elapses, which is a narrow window but achievable by any relayer polling aggressively; however, the consequence is trivial to work around (retry after a negligible delay) and does not compound into a lasting denial-of-service or fund-affecting condition.

### Recommendation
Align `verify_delay_passed` with the EVM `HandlerV2` semantics by using an inclusive comparison (`>=`) so that `current_timestamp - update_time == delay_period` is treated as elapsed, consistent with the challenge-period check used for EVM requests/timeouts.

### Proof of Concept
Not applicable as a fund-impacting exploit — the effect is a single rejected transaction that succeeds identically on resubmission after the timestamp advances by one unit.

Note: I was unable to find any reachable analog of this bug class in this codebase that produces the "concrete theft or permanent freezing of funds" impact required by the validation criteria (I checked `StreamingYieldVault`'s vesting/deposit-window boundaries, the `HandlerV2`/`ismp-core` timeout and challenge-period comparisons, the intents-coprocessor phantom bid window, and consensus client expiry/freeze logic — all other boundary comparisons I found were either already correctly inclusive or, where strict, erred on the side of safety rather than denying legitimate, fund-relevant actions). Given the rules require Medium/High/Critical impact with concrete fund/protocol consequences and reject "no-impact analogs," this finding is reported for completeness but likely falls short of the required severity bar.

### Citations

**File:** modules/ismp/core/src/handlers.rs (L104-114)
```rust
pub fn verify_delay_passed<H>(host: &H, proof_height: &StateMachineHeight) -> Result<bool, Error>
where
	H: IsmpHost,
{
	let update_time = host.state_machine_update_time(*proof_height)?;
	let delay_period = host
		.challenge_period(proof_height.id)
		.ok_or(Error::ChallengePeriodNotConfigured { state_machine: proof_height.id })?;
	let current_timestamp = host.timestamp();
	Ok(delay_period.as_secs() == 0 || current_timestamp.saturating_sub(update_time) > delay_period)
}
```

**File:** modules/ismp/core/src/handlers.rs (L121-145)
```rust
pub fn validate_state_machine<H>(
	host: &H,
	proof_height: StateMachineHeight,
) -> Result<Box<dyn StateMachineClient>, Error>
where
	H: IsmpHost,
{
	// Ensure consensus client is not frozen
	let consensus_client_id = host.consensus_client_id(proof_height.id.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized {
			consensus_state_id: proof_height.id.consensus_state_id,
		},
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	// Ensure client is not frozen
	host.is_consensus_client_frozen(proof_height.id.consensus_state_id)?;

	// Ensure delay period has elapsed
	if !verify_delay_passed(host, &proof_height)? {
		return Err(Error::ChallengePeriodNotElapsed {
			state_machine_id: proof_height.id,
			current_time: host.timestamp(),
			update_time: host.state_machine_update_time(proof_height)?,
		});
	}
```

**File:** evm/src/core/HandlerV2.sol (L181-186)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

```
