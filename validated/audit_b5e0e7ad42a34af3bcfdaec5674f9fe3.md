## Analog Found

### Title
Permissionless message delivery can front-run a fisherman's `veto_state_commitment`/`deleteStateMachineCommitment`, forcing forged message delivery from a fraudulent state commitment before it can be corrected - ([File: evm/src/core/HandlerV2.sol])

### Summary
Hyperbridge's optimistic-bridging design relies on a challenge period during which a permissioned "fisherman" can veto a fraudulent `StateCommitment` before it is used. However, once the challenge period elapses, *any* unprivileged relayer may permissionlessly deliver messages proven against that commitment in the very same block the period elapses. The veto transaction is a separate, non-atomic call that must land strictly before that delivery to have any effect — exactly the same "corrective admin action can be front-run" bug class as `setAmicableResolution` in the reference report, where an unprivileged actor races the corrective transaction and wins, making the correction a no-op.

### Finding Description
`HandlerV2.sol::handlePostRequests` (and its siblings `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`) are explicitly permissionless ("can be called by anyone") and gate only on the challenge period having elapsed: [1](#0-0) 

The check `challengePeriod > delay` allows dispatch the instant `delay == challengePeriod`, i.e. as soon as the window closes, with no additional buffer. On the Substrate side the same pattern is enforced by `verify_delay_passed`: [2](#0-1) 

The only defense against a fraudulent commitment surviving to be used is a fisherman vetoing it before the window closes, via `pallet_fishermen::veto_state_commitment` (Substrate) or the equivalent handler-only `deleteStateMachineCommitment`/`deleteStateMachineCommitmentInternal` path on the EVM host: [3](#0-2) [4](#0-3) 

The veto is its own transaction/extrinsic that competes for block space with any relayer's `handlePostRequests`/`handle` call built on the same (fraudulent) commitment. There is no mechanism forcing the veto to be processed before delivery transactions targeting the same height — dispatch of the underlying message (`host.dispatchIncoming`) is irreversible once it executes, and once a request receipt is stored, the veto can no longer undo the already-delivered side effects; it can only delete the commitment to prevent *future* use: [5](#0-4) 

This exactly mirrors the `setAmicableResolution` front-running pattern: a privileged/corrective transaction (the admin's outcome override / here, the fisherman's veto) exists specifically to override or invalidate an undesired outcome, but an unprivileged actor (a relayer motivated to get a fraudulent message delivered, or simply racing for relayer-fee rewards) can submit the competing permissionless transaction first and render the corrective action ineffective.

### Impact Explanation
If a relayer front-runs the veto and delivers a POST request or GET response proven against a byzantine/fraudulent `StateCommitment` before the fisherman's veto lands, the destination application (`IApp.onAccept`) executes with attacker-controlled, forged data. Depending on the app, this can mean unbacked minting via token-bridge apps, unauthorized `HostManager` governance actions, or fund release through `IntentGatewayV2`/escrow logic — i.e. forged message delivery and permanent freezing/theft of funds, since the veto cannot claw back an already-dispatched call. This satisfies the "forged message delivery / unsound state commitment" acceptance criteria.

### Likelihood Explanation
The race is realistic and even incentivized: relayers are financially rewarded for delivering messages (fee/reward accounting), so they are actively watching for the exact block/timestamp the challenge period elapses and submitting immediately — the same instant a fisherman would need to land a veto. Because the delivery check uses a strict boundary (`delay == challengePeriod` already qualifies) with no extra safety margin or priority given to veto transactions on the EVM side (unlike the Substrate `PrioritizeVeto` transaction-priority extension used for `pallet_fishermen`, seen in the simtest below, there is no equivalent guarantee on the EVM `HandlerV2` path), an attacker-controlled or bribed relayer has a straightforward opportunity to win this race on EVM destinations. [6](#0-5) 

Notably, this Substrate-side priority extension shows the team already anticipated this race for Substrate but the parallel guarantee is absent for the EVM `HandlerV2` delivery path where any relayer can call `handlePostRequests` at the exact same block the challenge period ends with no priority boost given to pending vetoes/fraud-proof transactions competing for the same block.

### Recommendation
- Do not allow the delivery window to open at the exact instant the veto window closes; require the delivery check to use `>=` with an added buffer/minimum number of blocks after challenge-period elapse before permissionless delivery is possible, giving vetoes deterministic priority.
- On the EVM host, add a mechanism analogous to Substrate's `PrioritizeVeto` transaction ordering so any pending veto/fraud-proof for the referenced height/commitment is guaranteed to be included and executed before same-block delivery transactions targeting that commitment.
- Consider requiring `deleteStateMachineCommitment`/veto calls to also invalidate any request/response receipts stored during the same challenge period tied to the vetoed height, if this is discovered after delivery, so downstream apps can be notified.

### Proof of Concept
1. A byzantine/eclipsed consensus proof causes a fraudulent `StateCommitment` to be stored for `height` via `storeStateMachineCommitment` on `EvmHost` (handler-only), starting its challenge period.
2. A fisherman detects the fraud and prepares a veto transaction to call `deleteStateMachineCommitmentInternal`/`veto_state_commitment` for `height`.
3. Concurrently, a relayer (potentially the same attacker who forged the consensus proof) prepares `HandlerV2.handlePostRequests` with a fraudulent `PostRequest` proven via `overlayRoot` at `height`, targeting a token-bridge or intents app.
4. As soon as `block.timestamp - stateMachineCommitmentUpdateTime(height) == challengePeriod` (the exact boundary in `evm/src/core/HandlerV2.sol` lines 182-185), the relayer submits `handlePostRequests` with higher gas/priority than the fisherman's veto.
5. `handlePostRequests` succeeds, calling `host.dispatchIncoming` and executing `onAccept` on the destination app with the forged request — minting tokens or moving funds — before the veto transaction is mined.
6. The veto transaction then executes, deleting the state commitment, but the forged message has already been irreversibly delivered and its effects (minted tokens, drained funds) persist.

### Citations

**File:** evm/src/core/HandlerV2.sol (L181-210)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
    }
```

**File:** modules/ismp/core/src/handlers.rs (L103-114)
```rust
/// for the state machine has elasped.
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

**File:** modules/pallets/fishermen/src/lib.rs (L165-193)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight((<T as frame_system::Config>::DbWeight::get().reads_writes(1, 2), Pays::No))]
		pub fn veto_state_commitment(
			origin: OriginFor<T>,
			height: StateMachineHeight,
		) -> DispatchResult {
			let account = ensure_signed(origin)?;
			ensure!(T::IsCollator::contains(&account), Error::<T>::UnauthorizedAction);

			let ismp_host = <T as Config>::IsmpHost::default();
			let commitment =
				ismp_host.state_machine_commitment(height).map_err(|_| Error::<T>::VetoFailed)?;
			ismp_host.delete_state_commitment(height).map_err(|_| Error::<T>::VetoFailed)?;

			Self::deposit_event(Event::StateCommitmentVetoed {
				height,
				commitment,
				fisherman: account.clone(),
			});
			pallet_ismp::Pallet::<T>::deposit_event(
				ismp::events::Event::StateCommitmentVetoed(StateCommitmentVetoed {
					height,
					fisherman: account.as_ref().to_vec(),
				})
				.into(),
			);

			Ok(())
		}
```

**File:** evm/src/core/EvmHost.sol (L701-732)
```text
    /**
     * @dev Delete the state commitment at given state height.
     */
    function deleteStateMachineCommitment(StateMachineHeight memory height, address fisherman)
        external
        restrict(_hostParams.handler)
    {
        deleteStateMachineCommitmentInternal(height, fisherman);
    }

    /**
     * @dev Delete the state commitment at given state height.
     */
    function deleteStateMachineCommitmentInternal(StateMachineHeight memory height, address fisherman) internal {
        StateCommitment memory stateCommitment = _stateCommitments[height.stateMachineId][height.height];
        delete _stateCommitments[height.stateMachineId][height.height];
        delete _stateCommitmentsUpdateTime[height.stateMachineId][height.height];
        // technically any state commitment can be vetoed, safety check that it's the latest before resetting it.
        if (_latestStateMachineHeight[height.stateMachineId] == height.height) {
            _latestStateMachineHeight[height.stateMachineId] = 1;
        }

        // track the fisherman responsible for rewards on hyperbridge through state proofs
        _vetoes[height.stateMachineId][height.height] = fisherman;

        emit StateCommitmentVetoed({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId),
            stateCommitment: stateCommitment,
            height: height.height,
            fisherman: fisherman
        });
    }
```

**File:** parachain/simtests/src/pallet_fishermen.rs (L271-317)
```rust
	// Then submit Alice's veto. Despite arriving second, the priority
	// extension must put it before Bob's remark in the next block.
	let veto_call = subxt::dynamic::tx(
		"Fishermen",
		"veto_state_commitment",
		vec![state_machine_height_to_value(&height)],
	);
	let alice_ss58 = Keyring::Alice.to_account_id().to_ss58check();
	let alice_call_data = client.tx().call_data(&veto_call)?;
	let alice_ext: Bytes = rpc_client
		.request("simnode_authorExtrinsic", rpc_params![Bytes::from(alice_call_data), alice_ss58])
		.await?;
	let alice_progress = SubmittableTransaction::from_bytes(client.clone(), alice_ext.0)
		.submit_and_watch()
		.await?;

	// Author one block, finalize.
	let block: CreatedBlock<H256> =
		rpc_client.request("engine_createBlock", rpc_params![true, false]).await?;
	let finalized: bool =
		rpc_client.request("engine_finalizeBlock", rpc_params![block.hash]).await?;
	assert!(finalized);
	bob_progress.wait_for_finalized_success().await?;
	alice_progress.wait_for_finalized_success().await?;

	// Inspect the block body. The veto extrinsic must come before the remark.
	let block_at = client.blocks().at(block.hash).await?;
	let extrinsics = block_at.extrinsics().await?;

	let mut veto_idx: Option<usize> = None;
	let mut remark_idx: Option<usize> = None;
	for (i, ext) in extrinsics.iter().enumerate() {
		let pallet = ext.pallet_name()?;
		let call = ext.variant_name()?;
		if pallet == "Fishermen" && call == "veto_state_commitment" {
			veto_idx = Some(i);
		}
		if pallet == "System" && call == "remark" {
			remark_idx = Some(i);
		}
	}
	let veto_idx = veto_idx.ok_or_else(|| anyhow!("veto extrinsic missing from block"))?;
	let remark_idx = remark_idx.ok_or_else(|| anyhow!("remark extrinsic missing from block"))?;
	assert!(
		veto_idx < remark_idx,
		"veto (idx {veto_idx}) must come before remark (idx {remark_idx}) due to PrioritizeVeto",
	);
```
