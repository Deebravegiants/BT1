## Analysis Result

**Analog confirmed.** The Hyperbridge protocol has the same bug class as the APISIX finding: a security-critical verification gate ("wait for fraud-proof challenge window") is **off by default**, and only becomes active if an operator/admin explicitly opts in — exactly like `ssl_verify` defaulting to `false` in openid-connect.

### Title
Challenge period (fraud-proof window) defaults to zero, disabling fishermen veto protection for consensus updates - ([File: evm/src/core/HandlerV2.sol])

### Summary
Hyperbridge's optimistic security model relies on a configurable `challengePeriod`/`challenge_period`: after a consensus update finalizes new `StateCommitment`s, relayers must wait for this period before delivering requests/responses, giving "fishermen" a chance to detect fraud and veto (freeze) the consensus client. Both `HandlerV2` on EVM and `pallet-ismp`'s delay check treat `challengePeriod == 0` as "no delay required," and every shipped deployment path (Foundry deploy script, Tron migration, parachain genesis config) initializes this value to `0`.

### Finding Description
The delay check is explicitly short-circuited when the period is zero: [1](#0-0) [2](#0-1) 

The same "zero disables the check" logic exists in the Substrate ISMP core: [3](#0-2) 

And this zero value is exactly what production deployment tooling ships as the default: [4](#0-3) [5](#0-4) [6](#0-5) 

The protocol documentation itself confirms the challenge period is the load-bearing safety mechanism that gives fishermen time to submit fraud proofs before relayers act on a state commitment: [7](#0-6) 

An admin/governance action (`update_consensus_state` on Substrate, or `updateHostParams` via the `HostManager` on EVM) is required to raise this above zero: [8](#0-7) 

Until that opt-in configuration happens, any state machine pair defaults to zero delay — identical in spirit to `ssl_verify=false` requiring an admin to opt in to the secure setting.

### Impact Explanation
With `challengePeriod == 0`, `HandlerV2.handlePostRequests`, `handleGetResponses`, and both timeout handlers allow relayers to deliver/execute messages against a freshly-submitted consensus state **the instant it lands on-chain**, with zero window for fishermen to detect and veto a fraudulent/byzantine consensus proof (double-signing, eclipse attack, faulty SP1/ECDSA BEEFY proof, etc.). This defeats the "optimistic verification + fraud proof" security model documented for the protocol and turns what should be a defense-in-depth delay into a no-op, allowing forged message delivery to be finalized before any fraud proof can freeze the consensus client.

### Likelihood Explanation
High for any state machine relationship left at the shipped default (0). The bug requires no attacker action beyond exploiting an already-compromised or faulty consensus proof; the missing safety margin removes the intended detection/veto window entirely rather than merely weakening it, and the default is baked into every current deployment script and the parachain genesis config, so it applies unless every single operator remembers to override it via governance.

### Recommendation
Change the default to a nonzero, protocol-appropriate challenge period in `DeployIsmp.s.sol`, the Tron migration, and the parachain genesis config, and consider treating `0` as "unconfigured" (reject/require an explicit minimum) in `HandlerV2` and `pallet-ismp`'s delay check rather than as "no delay required."

### Proof of Concept
1. Deploy `EvmHost` via `DeployIsmp.s.sol` (or the Tron migration) using the shipped defaults — `challengePeriod: 0`.
2. Submit a consensus proof via `HandlerV2.handleConsensus`, producing new `IntermediateState`s/`StateCommitment`s.
3. Immediately (same block) call `handlePostRequests`/`handleGetResponses` with a proof against the new commitment: `delay = 0`, so `challengePeriod != 0 && challengePeriod > delay` evaluates false and `ChallengePeriodNotElapsed` never reverts — the message is dispatched with no fraud-proof window having elapsed, exactly as the APISIX report describes an unauthenticated cleartext channel proceeding because the verify flag defaulted off.

### Citations

**File:** evm/src/core/HandlerV2.sol (L181-186)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

```

**File:** evm/src/core/HandlerV2.sol (L217-221)
```text
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
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

**File:** evm/script/DeployIsmp.s.sol (L126-138)
```text
        // EvmHost
        HostParams memory params = HostParams({
            uniswapV2: uniswapV2,
            admin: admin,
            hostManager: address(manager),
            handler: address(handler),
            unStakingPeriod: 21 * (60 * 60 * 24),
            challengePeriod: 0,
            consensusClient: address(consensusClient),
            hyperbridge: hyperbridge,
            feeToken: feeToken,
            stateMachines: stateMachines
        });
```

**File:** evm/tron/migrations/2_deploy_ismp.js (L156-171)
```javascript
    // HostParams struct — field order must match the Solidity struct definition
    const hostParams = [
        DEFAULT_TIMEOUT, // defaultTimeout
        defaultPerByteFee.toString(), // defaultPerByteFee
        stateCommitmentFee.toString(), // stateCommitmentFee
        feeToken, // feeToken
        admin, // admin
        handler.address, // handler
        hostManager.address, // hostManager
        uniswapV2, // uniswapV2
        UNSTAKING_PERIOD, // unStakingPeriod
        0, // challengePeriod
        consensusRouter.address, // consensusClient
        stateMachines, // stateMachines
        perByteFees, // perByteFees
        hyperbridge, // hyperbridge
```

**File:** modules/ismp/clients/parachain/client/src/lib.rs (L268-291)
```rust
	#[pallet::genesis_build]
	impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
		fn build(&self) {
			Pallet::<T>::initialize();
			let host = <T::IsmpHost>::default();
			let host_state_machine = host.host_state_machine();

			// insert the parachain ids
			for para in &self.parachains {
				Parachains::<T>::insert(para.id, ());
				let state_id = match host.host_state_machine() {
					StateMachine::Kusama(_) => StateMachine::Kusama(para.id),
					StateMachine::Polkadot(_) => StateMachine::Polkadot(para.id),
					_ => continue,
				};
				let _ = host.store_challenge_period(
					StateMachineId {
						state_id,
						consensus_state_id: parachain_consensus_state_id(host_state_machine),
					},
					0,
				);
			}
		}
```

**File:** docs/content/protocol/ismp/consensus.mdx (L206-219)
```text
### `StateMachineUpdated`

```rust showLineNumbers
/// Emitted when a state machine is successfully updated to a new height
struct StateMachineUpdated {
    /// State machine height
    state_machine_id: StateMachineId,
    /// State machine latest height
    latest_height: u64,
}
```

A `StateMachineUpdated` event is emitted to notify network participants (both relayers and fishermen) of some newly available `StateCommitment`s for a given state machine. Relayers will wait for the configured `challenge_period` before attempting to transmit new requests & responses. While fishermen will check if these pending `StateCommitment`s describe valid states on the counterparty network. If the `challenge_period` elapses without any fraud proofs being presented, we can safely conclude that the provided `StateCommitment`s are indeed canonical.

```

**File:** modules/pallets/ismp/src/lib.rs (L410-437)
```rust
		/// Modify the unbonding period and challenge period for a consensus state.
		/// The dispatch origin for this call must be `T::AdminOrigin`.
		///
		/// - `message`: `UpdateConsensusState` struct.
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().writes(2))]
		#[pallet::call_index(3)]
		pub fn update_consensus_state(
			origin: OriginFor<T>,
			message: UpdateConsensusState,
		) -> DispatchResult {
			T::AdminOrigin::ensure_origin(origin)?;

			let host = Pallet::<T>::default();

			if let Some(unbonding_period) = message.unbonding_period {
				host.store_unbonding_period(message.consensus_state_id, unbonding_period)
					.map_err(|_| Error::<T>::UnbondingPeriodUpdateFailed)?;
			}

			for (state_id, period) in message.challenge_periods {
				let id =
					StateMachineId { state_id, consensus_state_id: message.consensus_state_id };
				host.store_challenge_period(id, period)
					.map_err(|_| Error::<T>::UnbondingPeriodUpdateFailed)?;
			}

			Ok(())
		}
```
