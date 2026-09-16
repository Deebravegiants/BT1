### Title
Consensus clients accept externally-signed header timestamps as `StateCommitment.timestamp` with no wall-clock upper bound, enabling premature timeout evasion / delayed-freeze — ([File: modules/ismp/clients/bsc/src/lib.rs])

### Summary
Multiple Hyperbridge consensus-client implementations (`BscClient`, `PharosClient`, GRANDPA parachain client, `TendermintClient`) copy the untrusted, source-chain-embedded block header `timestamp` field directly into the `StateCommitment.timestamp` that Hyperbridge stores and later relies on for request-timeout evaluation — with no check that this timestamp is bounded above by the host's own wall clock (`host.timestamp()`). This mirrors the reported nimiq-blockchain bug class: a lower-bound-only (or no-bound) timestamp check that permits a validator/producer-controlled value to diverge arbitrarily from real time.

### Finding Description
In `modules/ismp/clients/bsc/src/lib.rs` (`verify_consensus`, lines 127-144), the finalized header's `timestamp` field — taken straight from the BSC header decoded and hash-verified by `verify_bsc_header` — is placed unchecked into `StateCommitment.timestamp`: [1](#0-0) 

The same unchecked pattern exists in Pharos: [2](#0-1) 

And GRANDPA (deriving `timestamp` from the parachain header digest/slot, again with no bound check against `host.timestamp()`): [3](#0-2) 

`verify_bsc_header` (`modules/consensus/bsc/verifier/src/lib.rs`) validates BLS signatures, vote data, adjacency, and epoch rotation, but never validates `header.timestamp` against any bound — it is not even referenced in the verification logic. The consuming client (`modules/ismp/clients/bsc/src/lib.rs`) also never compares `finalized_header.timestamp` to `host.timestamp()`. Consequently, a source-chain validator supermajority (reachable analog: a relayer submitting a validly-signed but timestamp-manipulated consensus proof via `ConsensusMessage`) can push `StateCommitment.timestamp` arbitrarily into the future.

This commitment timestamp is exactly what downstream request/timeout logic treats as authoritative "destination/source time." On the EVM side, `HandlerV2.sol`'s `handlePostRequestTimeouts`/`handleGetRequestTimeouts` compare `request.timeout()` against `state.timestamp` (the stored `StateCommitment.timestamp`), not the EVM `block.timestamp`: [4](#0-3) [5](#0-4) 

The pallet-ismp `IsmpHost` trait documents `state_machine_commitment` as authoritative state, and `update_client` in `modules/ismp/core/src/handlers/consensus.rs` stores whatever the consensus client returns without any sanity check against `host.timestamp()`: [6](#0-5) 

By contrast, the Tendermint client's underlying `cometbft_light_client_verifier` library does enforce a `clock_drift`-bounded future-timestamp check (`HeaderFromFuture` error) inside `verify_update_header`, so Tendermint is not vulnerable here — but BSC, Pharos, and the GRANDPA/parachain slot-derived timestamp path have no equivalent bound.

### Impact Explanation
Since the `StateCommitment.timestamp` (sourced from the unchecked header timestamp) is the value used to decide whether a `PostRequest`/`GetRequest` has "timed out" for these state machines' finalized state commitments, a validator set capable of producing a signed header with a future timestamp can make Hyperbridge/relayers believe more time has elapsed at the destination than actually has. This can be used to prematurely trigger request-timeout processing (`handlePostRequestTimeouts`/`handleGetRequestTimeouts`, or `pallet-ismp`'s equivalent Post-timeout path) before the request was genuinely undeliverable, refunding relayer fees and effectively cancelling in-flight cross-chain messages that a legitimate destination module might still be processing — a form of unauthorized state/fund manipulation reachable via a single relayed consensus proof plus a subsequently relayed timeout proof, matching the "route unable to deliver messages" / "forged message delivery" criteria.

### Likelihood Explanation
Exploitation requires control (or collusion) over the source chain's validator supermajority (BSC 2/3 BLS quorum, or the relevant relay authority set for GRANDPA/Pharos) to produce a legitimately-signed header carrying a manipulated timestamp — this is a real-world constraint but is exactly the threat model the original CVE targets (a malicious block-producing validator). Given BSC/Pharos are permissioned/limited validator sets, and no additional Hyperbridge-side bound exists to catch this, likelihood is non-trivial for any of these integrated chains whose validator set can be compromised or colludes, and the check is trivial to add (as Tendermint already effectively has via clock-drift).

### Recommendation
Add an explicit upper-bound check on the header/finalized-block timestamp in each consensus client's `verify_consensus` before constructing `StateCommitmentHeight` — e.g., reject if `finalized_header.timestamp > host.timestamp() + MAX_CLOCK_DRIFT` — for `BscClient`, `PharosClient`, and the GRANDPA/parachain digest-timestamp path, mirroring the `clock_drift` bound already enforced transitively for Tendermint. Also consider bounding `header.timestamp >= trusted_state`'s previous finalized timestamp to prevent regression.

### Proof of Concept
1. Attacker controls (or colludes with) ≥2/3 of the BSC validator set (or the relevant Pharos/GRANDPA authority set).
2. Attacker produces a validly BLS-signed `BscClientUpdate` (or Pharos/GRANDPA equivalent) whose `finalized_header.timestamp` is set far into the future (e.g., years ahead) while all other header fields (state_root, parent hash, vote data) remain internally consistent and pass `verify_bsc_header`'s checks.
3. Attacker/relayer submits this as a `ConsensusMessage` to `update_client` (`modules/ismp/core/src/handlers/consensus.rs`), which calls `BscClient::verify_consensus`; the future timestamp is accepted unchecked and stored as `StateCommitment.timestamp`.
4. Attacker (or any relayer) then submits a `PostRequestTimeoutMessage`/`GetTimeoutMessage` referencing this state commitment height; `HandlerV2.sol`'s `handlePostRequestTimeouts` compares `request.timeout()` against the forged `state.timestamp`, which now already exceeds the request's `timeout_timestamp`, allowing the timeout to be processed even though real elapsed time has not reached the timeout window — refunding fees and cancelling the request prematurely.

### Citations

**File:** modules/ismp/clients/bsc/src/lib.rs (L137-144)
```rust
		let state_commitment = StateCommitmentHeight {
			commitment: StateCommitment {
				timestamp: finalized_header.timestamp,
				overlay_root: None,
				state_root: finalized_header.state_root,
			},
			height: finalized_header.number.low_u64(),
		};
```

**File:** modules/ismp/clients/pharos/src/lib.rs (L120-127)
```rust
		let state_commitment = StateCommitmentHeight {
			commitment: StateCommitment {
				timestamp: update.header.timestamp,
				overlay_root: None,
				state_root: update.header.state_root,
			},
			height: new_state.finalized_block_number,
		};
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L132-152)
```rust
					for header in header_vec {
						let digest_result =
							fetch_overlay_root_and_timestamp(header.digest(), slot_duration)?;

						let height: u32 = (*header.number()).into();

						let intermediate = match T::Coprocessor::get() {
							Some(id) if id == state_id => StateCommitmentHeight {
								// for the coprocessor, we only care about the child root & mmr root
								commitment: StateCommitment {
									timestamp: digest_result.timestamp,
									overlay_root: Some(digest_result.ismp_digest.mmr_root),
									state_root: digest_result.ismp_digest.child_trie_root, /* child root */
								},
								height: height.into(),
							},
							_ => StateCommitmentHeight {
								commitment: StateCommitment {
									timestamp: digest_result.timestamp,
									overlay_root: Some(digest_result.ismp_digest.child_trie_root),
									state_root: header.state_root,
```

**File:** evm/src/core/HandlerV2.sol (L258-271)
```text
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            PostRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

```

**File:** evm/src/core/HandlerV2.sol (L293-306)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            GetRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L41-70)
```rust
	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
	let timestamp = host.timestamp();
	host.store_consensus_update_time(msg.consensus_state_id, timestamp)?;
	let mut state_updates = vec![];
	for (id, mut commitment_heights) in intermediate_states {
		commitment_heights.sort_unstable_by(|a, b| a.height.cmp(&b.height));
		let previous_latest_height = host.latest_commitment_height(id)?;
		let mut last_commitment_height = None;
		for commitment_height in commitment_heights.iter() {
			let state_height = StateMachineHeight { id, height: commitment_height.height };

			// Only allow heights greater than latest height
			if previous_latest_height > commitment_height.height {
				continue;
			}

			// Skip duplicate states
			if host.state_machine_commitment(state_height).is_ok() {
				continue;
			}

			last_commitment_height = Some(state_height);
			host.store_state_machine_commitment(state_height, commitment_height.commitment)?;
			host.store_state_machine_update_time(state_height, host.timestamp())?;
```
