### Title
Fisherman veto (`deleteStateMachineCommitment`) can permanently strand in-flight messages proven against the vetoed height, freezing user funds - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.deleteStateMachineCommitment` / `deleteStateMachineCommitmentInternal` permanently deletes a `StateCommitment` (the `overlayRoot`/`stateRoot` — the ISMP analog of the Footium "merkle root") for a given `StateMachineHeight`, with no check for whether requests, responses, or timeouts that were already dispatched on the source chain against that specific height have been relayed and processed yet. [1](#0-0) 

### Finding Description
`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` in `HandlerV2` all read `host.stateMachineCommitment(height)` for a specific height and revert with `StateCommitmentNotFound` if the stored root/state at that height is empty: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

These are exactly the same "claim" style entry points as the `claimETHPrize`/`claimERC20Prize` functions in the referenced report — an unprivileged relayer/user reaches them to deliver an already-committed message (a request, response, or timeout) by proving it against the commitment stored for its height.

`storeStateMachineCommitment` writes the commitment for a height, but `deleteStateMachineCommitmentInternal` can erase it later: [6](#0-5) [7](#0-6) 

The deletion is unconditional — it does not check whether any post requests/responses/timeouts destined for/originating from that height are still pending relay. Once vetoed, `_stateCommitments[stateMachineId][height]` is zeroed out; any relayer later attempting to deliver a message with `proof.height == height` will hit `StateCommitmentNotFound` (post requests / get responses) or `state.stateRoot == bytes32(0)` (timeouts), permanently preventing delivery of those messages. Because messages/requests were already dispatched and committed on the source chain based on the (now-deleted) commitment, and there is no mechanism to re-derive or replace that specific height's commitment (the height is now "spent" - `_latestStateMachineHeight` is only reset to `1` if it was the latest, not restored to a usable prior value), any message proven exclusively against that height is stuck forever.

This mirrors the report's core defect precisely: a privileged-but-not-arbitrary party (the fisherman-triggered veto path, gated only by `restrict(_hostParams.handler)`) can invalidate the "root" (state commitment) that unprivileged relayers/apps rely on to claim/deliver already-dispatched value-bearing messages, with no guarantee that all in-flight messages proven against that root have been processed first.

### Impact Explanation
Any POST request, GET response, or timeout message that was dispatched/committed while a given `StateMachineHeight`'s commitment was live, but not yet relayed and delivered before that commitment is vetoed, becomes permanently undeliverable. Since token bridge and intents flows on Hyperbridge (mint/burn, escrow settlement, fee/reward payouts) are driven by successful delivery of these ISMP messages, this results in permanent freezing of the underlying funds/assets tied to those messages — matching the "route unable to deliver messages" / "permanent freezing of funds" acceptance bar.

### Likelihood Explanation
The veto path exists specifically to react to fraudulent/incorrect commitments (a legitimate byzantine-fault-handling feature), so it will be exercised in normal operation whenever fishermen detect an invalid state commitment. Because `deleteStateMachineCommitmentInternal` performs no check for outstanding, still-unrelayed messages proven at that height, any veto that occurs while legitimate messages are still in the relay pipeline for that height will strand them — this is a systemic, not merely theoretical, race between message delivery and veto processing, and requires no attacker other than normal operation of the fisherman/veto mechanism plus message timing.

### Recommendation
Before allowing a state commitment to be deleted, track and only permit the veto once no pending (undelivered) request/response/timeout messages remain committed against that specific height, or provide a remediation path (e.g., re-store a corrected commitment at the same height, or allow messages proven against a vetoed height to be recovered/replayed against a subsequent valid commitment) so users are not permanently locked out of already-dispatched funds.

### Proof of Concept
1. Source chain dispatches a `PostRequest` (e.g., a token-gateway mint/burn message) that gets included in the overlay tree committed at `StateMachineHeight{stateMachineId, height=H}` on the destination `EvmHost` via `storeStateMachineCommitment`. [6](#0-5) 
2. Before any relayer calls `handlePostRequests` with `proof.height == H` to deliver that request, a fisherman/handler triggers `deleteStateMachineCommitment(height, fisherman)` for height `H` (e.g., because a different, unrelated leaf in that height's overlay tree was found fraudulent). [1](#0-0) 
3. `_stateCommitments[stateMachineId][H]` is now zero. Any subsequent attempt to deliver the still-pending, legitimate request via `handlePostRequests` (or a pending response/timeout via `handleGetResponses`/`handlePostRequestTimeouts`) reverts with `StateCommitmentNotFound`, because `host.stateMachineCommitment(H).overlayRoot == bytes32(0)`. [2](#0-1) 
4. There is no code path to re-establish a commitment at height `H` for that `stateMachineId` (future commitments must be for heights greater than `_latestStateMachineHeight`), so the request/response/timeout — and any funds it represents — can never be delivered, resulting in permanent loss/freeze.

### Citations

**File:** evm/src/core/EvmHost.sol (L687-699)
```text
    function storeStateMachineCommitment(StateMachineHeight memory height, StateCommitment memory commitment)
        external
        restrict(_hostParams.handler)
    {
        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;

        emit StateMachineUpdated({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId), 
            height: height.height
        });
    }
```

**File:** evm/src/core/EvmHost.sol (L704-732)
```text
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

**File:** evm/src/core/HandlerV2.sol (L199-202)
```text
        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();
```

**File:** evm/src/core/HandlerV2.sol (L236-239)
```text
        bytes32 root = host.stateMachineCommitment(message.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
        if (!valid) revert InvalidProof();
```

**File:** evm/src/core/HandlerV2.sol (L263-264)
```text
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
```

**File:** evm/src/core/HandlerV2.sol (L299-300)
```text
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
```
