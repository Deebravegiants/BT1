### Title
Instant, retroactive `challengePeriod` reduction can bypass fishermen fraud-detection window, enabling forged state-commitment messages to be delivered before veto - ([File: evm/src/core/HandlerV2.sol])

### Summary
Hyperbridge's optimistic security model relies on a fixed "challenge window" between when a state commitment is recorded and when messages proven against it may be processed, giving fishermen time to detect and veto fraudulent commitments [1](#0-0) . However, the challenge-period value enforced at message-handling time is read live from mutable host params rather than being fixed at the time each state commitment was recorded, so an instant change to `challengePeriod` retroactively shortens (or removes) the safety window for commitments that are already pending, exactly mirroring the `overdueBlocks` bug class: a security-critical timing parameter can be changed after the fact and applied to obligations/commitments that were created under the old rule.

### Finding Description
When a state machine update is recorded, the host stores only the commitment and an update timestamp; it does not snapshot the challenge period that was in effect at that moment: [2](#0-1) 

All message handlers (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`) then gate on the *current* `host.challengePeriod()` value compared to the elapsed delay since that update time: [3](#0-2) [4](#0-3) 

`challengePeriod` is part of `HostParams`, which can be updated at any time by cross-chain governance (`hostManager`), with no restriction preventing the change from applying to commitments already in-flight: [5](#0-4) [6](#0-5) 

The identical pattern exists on the Substrate/pallet-ismp side: `verify_delay_passed` reads `host.challenge_period(proof_height.id)` — the currently configured value — rather than a value pinned to the specific commitment height: [7](#0-6) 

and `store_challenge_period` simply overwrites the stored value for a state machine with no regard for outstanding commitments still inside their original challenge window: [8](#0-7) 

The entire fishermen security model assumes a stable challenge window: fishermen watch counterparty state during that window and submit `veto_state_commitment` if fraud is detected, and relayers wait out the same window before submitting messages: [9](#0-8) [10](#0-9) 

If `challengePeriod` is reduced (including to `0`, which explicitly disables the check per `challengePeriod != 0 && ...`) after a state commitment has already been recorded but before fishermen have had the originally-promised window to review it, any relayer can immediately submit `handlePostRequests`/`handleGetResponses`/timeout messages proven against that commitment — even if it is fraudulent and would otherwise have been vetoed in time. The relayer-side tooling (`wait_for_challenge_period`) also queries the challenge period live and would similarly under-wait if it's shortened mid-flight: [11](#0-10) 

### Impact Explanation
This breaks the core safety invariant of Hyperbridge's optimistic consensus model: the challenge period is what makes it safe to trust an on-chain state commitment before slow, permissionless fraud-proofs exist (fishermen currently provide the only fraud-detection layer) [1](#0-0) . If the challenge period tied to an already-recorded, still-unreviewed commitment can be shortened after the fact, a forged/fraudulent state commitment can be used to deliver forged messages (mint/unlock funds, execute unauthorized app actions, or process fabricated timeouts) to `IsmpModule`s before fishermen can react and veto it, directly matching the "unsound state commitment" / "forged message delivery" impact class. This can result in theft of funds or unauthorized state transitions in any application relying on Hyperbridge's cross-chain proofs.

### Likelihood Explanation
Triggering the bug does not require malicious governance intent — it only requires a legitimate, routine reduction of `challengePeriod` (e.g., to speed up latency for a well-behaved chain) while some other state commitment is concurrently pending review, or a race where governance both submits a state commitment and shortly after (within the old challenge window) lowers the parameter for operational reasons. Because the parameter is global per state machine and applies to *all* pending commitments retroactively rather than only to new ones, any parameter tuning during normal operation creates this window, similar to how the referenced `overdueBlocks` finding does not require a malicious lender — any timely-but-unplanned change is sufficient to strand/expose obligations created under the old rule.

### Recommendation
- Snapshot the challenge period at the moment a state commitment/consensus update is stored (alongside `stateMachineCommitmentUpdateTime`), and use that snapshotted value — not the live `HostParams.challengePeriod` — when validating delay-elapsed checks in `HandlerV2.sol` and `verify_delay_passed` in `modules/ismp/core/src/handlers.rs`.
- Alternatively, make `challengePeriod` changes apply only to state commitments recorded after the update (i.e., versioned/height-indexed challenge periods), never to already-pending ones.
- Consider adding a timelock/delay to `updateHostParams`/`set_challenge_period` for the `challengePeriod` field specifically, giving fishermen and relayers time to adapt.

### Proof of Concept
1. Governance submits a legitimate `updateHostParams` reducing `challengePeriod` from `T` seconds to `0` (or a much smaller value) via the `hostManager` cross-chain path (`evm/src/core/HostManager.sol` `onAccept` → `IHostManager(_params.host).updateHostParams`).
2. Prior to this update, a state commitment at height `H` was recorded (honestly or fraudulently) with `stateMachineCommitmentUpdateTime(H) = t0`, intended to remain unusable until `t0 + T`.
3. Immediately after the parameter update lands, an attacker/relayer calls `handlePostRequests`/`handleGetResponses` with a proof against height `H`; the check `challengePeriod > delay` now uses the new (small/zero) `challengePeriod`, so it passes even though `t0 + T` has not elapsed and fishermen have not had their promised window to veto height `H`.
4. If height `H`'s commitment was fraudulent, the attacker successfully delivers a forged message to a downstream `IsmpModule` before any veto can land, since `pallet-fishermen::veto_state_commitment` only works while the commitment is still "in its challenge period" conceptually, but the enforced check on the delivery side no longer requires that original window.

### Citations

**File:** docs/content/protocol/interoperability/consensus-proofs.mdx (L138-146)
```text
### Optimistic Bridging

To prevent the damage that can be done to our bridge in the event of a byzantine attack, **we must introduce a challenge window in the form of a time delay between when consensus proofs are verified by our consensus client and when state proofs associated with those headers can be used to process cross-chain messages.**

During this challenge window, consensus clients can detect byzantine attacks. Off-chain consensus clients can do this by participating in the P2P network. On-chain consensus clients, on the other hand, will need to rely on off-chain parties, which we'll call fishermen<sup>[3]</sup>, to provide the proofs of fraud to the client.

These fishermen will need some incentive to watch for byzantine attacks and report the fraud proofs which will safeguard the consensus client. As such, we will require relayers who submit consensus proofs to be staked, in the event of byzantine attacks, relayer’s stake can be used to incentivise fishermen to submit fraud proofs.

In the event of a byzantine attack, the fraud proofs will allow for the consensus client to go into a frozen state until the source chain recovers from this byzantine state, **The host chain can then unfreeze the consensus client through some kind of on-chain governance, allowing the bridge to resume operations safely and without any loss of funds ever having occurred.**
```

**File:** evm/src/core/EvmHost.sol (L548-550)
```text
    function stateMachineCommitmentUpdateTime(StateMachineHeight memory height) external view returns (uint256) {
        return _stateCommitmentsUpdateTime[height.stateMachineId][height.height];
    }
```

**File:** evm/src/core/EvmHost.sol (L564-576)
```text
    /**
     * @dev Updates the HostParams. Only callable by cross-chain governance
     * via the configured `hostManager`. The admin has no privileges here —
     * environments that need a privileged admin override (testnets, forks)
     * should use `TestnetHost`, which extends this contract.
     *
     * Marked `virtual` so subclasses can broaden the authorization
     * @param params, the new host params.
     */
    function updateHostParams(HostParams memory params) external virtual restrict(_hostParams.hostManager) {
        updateHostParamsInternal(params);
    }

```

**File:** evm/src/core/EvmHost.sol (L623-636)
```text
        // safe to emit here because invariants have already been checked
        // and don't want to store a temp variable for the old params
        emit HostParamsUpdated({oldParams: _hostParams, newParams: params});

        _hostParams.feeToken = params.feeToken;
        _hostParams.admin = params.admin;
        _hostParams.handler = params.handler;
        _hostParams.hostManager = params.hostManager;
        _hostParams.uniswapV2 = params.uniswapV2;
        _hostParams.unStakingPeriod = params.unStakingPeriod;
        _hostParams.challengePeriod = params.challengePeriod;
        _hostParams.consensusClient = params.consensusClient;
        _hostParams.stateMachines = params.stateMachines;
        _hostParams.hyperbridge = params.hyperbridge;
```

**File:** evm/src/core/HandlerV2.sol (L181-186)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

```

**File:** evm/src/core/HandlerV2.sol (L254-260)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();
```

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

**File:** modules/pallets/ismp/src/host.rs (L293-300)
```rust
	fn store_challenge_period(
		&self,
		state_machine: StateMachineId,
		period: u64,
	) -> Result<(), Error> {
		ChallengePeriod::<T>::insert(state_machine, period);
		Ok(())
	}
```

**File:** docs/content/developers/explore/fishermen.mdx (L8-20)
```text
Every collator on Hyperbridge doubles as a fisherman. The fisherman task runs inside the collator binary and watches each connected L2 across multiple independent RPC providers. When those providers reach a supermajority agreeing on an L2 state that contradicts what Hyperbridge is about to commit to its state trie, the fisherman submits a `veto_state_commitment` extrinsic signed by the collator's AURA key. This veto prevents the fraudulent commitment from being finalised on Hyperbridge, protecting every application that relies on cross-chain state proofs.

Collators are compensated 2 `$BRIDGE` per block produced. This reward covers both block production and the ongoing cost of operating a high-quality fisherman setup — running premium RPC endpoints across multiple independent providers is part of the job, and the block reward is sized to make that sustainable.

## What a Fisherman Can Do

A fisherman holding a seat in the active collator set can:

- **Veto a state commitment** by calling `pallet-fishermen.veto_state_commitment` with a specific `StateMachineHeight`. The veto is accepted without requiring a cryptographic proof — the fisherman's inclusion in the collator set is the trust anchor.
- **Block cross-chain message delivery** for the vetoed height. Because a state commitment is an accumulator, messages from a vetoed height will still be included in a later commitment once the correct state is finalised. A veto delays processing; it cannot censor a specific message permanently.
- **Prevent a compromised or faulty consensus client** from anchoring fraudulent L2 state on Hyperbridge, which would otherwise let attackers fabricate state proofs and drain applications of funds.

A fisherman cannot selectively censor individual messages. The veto operates at the state commitment level — either the entire state at a given height is accepted or it is rejected.
```

**File:** docs/content/protocol/ismp/consensus.mdx (L218-232)
```text
A `StateMachineUpdated` event is emitted to notify network participants (both relayers and fishermen) of some newly available `StateCommitment`s for a given state machine. Relayers will wait for the configured `challenge_period` before attempting to transmit new requests & responses. While fishermen will check if these pending `StateCommitment`s describe valid states on the counterparty network. If the `challenge_period` elapses without any fraud proofs being presented, we can safely conclude that the provided `StateCommitment`s are indeed canonical.

### `StateCommitmentVetoed`

```rust showLineNumbers
/// Emitted when a `StateCommitment` has been successfully vetoed by a fisherman
pub struct StateCommitmentVetoed {
    /// The state commitment identifier
    pub height: StateMachineHeight,
    /// The account responsible
    pub fisherman: Vec<u8>,
}
```

A `StateCommitmentVetoed` event is emitted after a fisherman successfully vetoes a `StateCommitment` that is still within its challenge period. This instructs relayers to discard any pending requests/responses whose proofs rely on the vetoed commitment.
```

**File:** tesseract/messaging/primitives/src/lib.rs (L742-756)
```rust
pub async fn wait_for_challenge_period(
	client: Arc<dyn IsmpProvider>,
	last_consensus_update: Duration,
	counterparty_state_id: StateMachineId,
) -> anyhow::Result<()> {
	let challenge_period = client.query_challenge_period(counterparty_state_id).await?;
	if challenge_period != Duration::ZERO {
		log::info!(
			target: LOG_TARGET, "Waiting for challenge period {challenge_period:?} for {} on {}",
			counterparty_state_id.state_id,
			client.name()
		);
	}

	tokio::time::sleep(challenge_period).await;
```
