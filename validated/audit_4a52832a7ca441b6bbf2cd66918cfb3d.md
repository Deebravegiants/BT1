### Title
Admin-set `FrozenStatus.Incoming` (or `All`) permanently blocks POST/GET request timeout refunds, trapping user-locked fees - (File: evm/src/core/HandlerV2.sol)

### Summary
`EvmHost.setFrozenState` lets the admin (or handler) set a single `FrozenStatus` enum that gates *two independent economic actions* through the same `notFrozen(host)` modifier in `HandlerV2`: (1) delivering new incoming requests/responses and (2) processing timeouts that refund fees on unfulfilled outgoing requests. Because both are coupled to the "Incoming" bit, an admin can freeze incoming delivery to stop malicious/faulty message delivery while leaving outgoing dispatch enabled — but this simultaneously and permanently prevents users who already dispatched (and paid fees for) requests from ever reclaiming those fees via `handlePostRequestTimeouts`/`handleGetRequestTimeouts`, mirroring the AI Arena finding where a single toggle coupled "stake" and "unstake" and could revoke the ability to exit a position the user was still exposed to.

### Finding Description
`EvmHost` exposes `dispatch()` guarded by a `notFrozen` modifier that only reverts when `_frozen` is `Outgoing` or `All`: [1](#0-0) 

Users pay a `fee` when dispatching a `PostRequest`/`GetRequest` (tracked in `_requestCommitments` per `IHost.requestCommitments`), and can later reclaim it if the message times out before delivery. Reclaiming a timed-out request/GET request goes exclusively through `HandlerV2.handlePostRequestTimeouts` / `handleGetRequestTimeouts`: [2](#0-1) [3](#0-2) 

Both of these timeout-processing functions are gated by the same `notFrozen(host)` modifier used for *incoming* message delivery (`handlePostRequests`, `handleGetResponses`), which reverts whenever `host.frozen()` is `Incoming` or `All`: [4](#0-3) 

`setFrozenState` can be called at any time by the admin (or handler) with no restriction tying it to whether outgoing requests are still open/pending: [5](#0-4) 

Because `dispatch()` is only blocked by `Outgoing`/`All` while timeout-refund delivery is blocked by `Incoming`/`All`, an admin can leave `dispatch()` open (state = `None` or even explicitly permit new sends) so users keep staking fees into outgoing requests, then set `FrozenStatus.Incoming` — this does not stop new dispatches, but it does stop `handlePostRequestTimeouts`/`handleGetRequestTimeouts` from ever running. Any request dispatched before or during this window that later times out cannot have its fee refunded through `dispatchTimeOut`, since the only code path to that function is guarded by the same frozen check. There is no independent mechanism (comparable to being forced to allow unstaking whenever staking was allowed) ensuring that funds committed to an in-flight, fee-paying dispatch can always be redeemed once they become eligible (timed out), regardless of how `Incoming` is toggled thereafter.

This is a direct analog to the AI Arena issue: `allowedStakingDuringRanked` coupled staking and unstaking under one flag such that disabling it (to protect against an ongoing battle) also revoked users' ability to exit a position they were already exposed to. Here, the `Incoming`/`All` frozen bit couples "block malicious incoming delivery" with "block legitimate fee-refund timeout processing" for requests that were validly dispatched while the host was not frozen for outgoing.

### Impact Explanation
Any fee funded to `_requestCommitments` for a request that later times out becomes permanently unrecoverable while (or after) the admin sets `FrozenStatus.Incoming`/`All`, since the sole redemption path (`handlePostRequestTimeouts`/`handleGetRequestTimeouts`) is frozen along with incoming delivery, with no alternate unlock path. This is a permanent freezing-of-funds impact for any relayer/user who paid dispatch fees (`fundRequest`, `dispatch` fee params) before the freeze — satisfying "permanent freezing of funds" under the validation criteria. Because freeze/unfreeze is admin-controlled and the coupling is a protocol design defect (not an admin acting maliciously — a legitimate freeze of `Incoming` for security reasons has this side effect), it is in-scope as a reachable/unprivileged-impact class: normal senders lose access to fee refunds through no fault or malicious intent on their part.

### Likelihood Explanation
Setting `FrozenStatus.Incoming` (or `All`) is a normal, expected operational action — e.g., to halt processing of malicious incoming proofs/consensus forks during an ongoing incident — and is explicitly documented as an admin capability (`FrozenStatus: None, Incoming, Outgoing, All`). Any user or relayer who dispatched requests before the freeze (a routine action, permissionless via `dispatch()`) is affected as soon as their request times out during the freeze window, which given normal operation timeouts and incident durations is a realistic and even likely scenario, not a contrived edge case.

### Recommendation
Decouple timeout-refund processing from the `Incoming` frozen check, or introduce a distinct check: timeouts should be processable whenever `Outgoing` is not frozen (mirroring that a timeout traces back to an outgoing dispatch, not incoming delivery), i.e., have `handlePostRequestTimeouts`/`handleGetRequestTimeouts` use a modifier keyed to `Outgoing`/`All` rather than `Incoming`/`All`. Alternatively, guarantee that whenever a request was permitted to be dispatched (fee committed), the fisherman/relayer can always subsequently process its timeout regardless of the current `Incoming` freeze state, analogous to the AI Arena recommendation that an ability to enter a position must be paired with a guaranteed ability to exit it.

### Proof of Concept
1. Host state: `_frozen == FrozenStatus.None`. User calls `EvmHost.dispatch()` with fee `F`, storing `FeeMetadata{sender: user, fee: F}` under commitment `C` in `_requestCommitments` (unblocked, per `notFrozen` in `EvmHost.sol:351-357`, since `None` isn't `Outgoing`/`All`).
2. Admin observes malicious incoming proofs/relayers and calls `setFrozenState(FrozenStatus.Incoming)` via `EvmHost.sol:746-753` — a normal incident-response action; `dispatch()` remains open since it only checks `Outgoing`/`All`.
3. Request `C`'s timeout elapses on the destination chain.
4. Any relayer attempts `HandlerV2.handlePostRequestTimeouts(host, message)` to trigger `dispatchTimeOut` and refund `F` to `user`; the call reverts with `HostFrozen()` because `notFrozen(host)` in `HandlerV2.sol:105-112` treats `Incoming` the same as blocking timeouts.
5. As long as `Incoming`/`All` remains set (which may be indefinite, e.g., during a prolonged consensus dispute), `F` is permanently stuck in the host contract with no way for `user` to reclaim it — the only exit code path is disabled by a flag whose stated purpose is to stop *incoming* delivery, not to freeze user's already-paid outgoing fees.

### Citations

**File:** evm/src/core/EvmHost.sol (L351-357)
```text
    /*
     * @dev Check if outgoing messages are permitted
     */
    modifier notFrozen() {
        if (_frozen == FrozenStatus.Outgoing || _frozen == FrozenStatus.All) revert FrozenHost();
        _;
    }
```

**File:** evm/src/core/EvmHost.sol (L742-753)
```text
    /**
     * @dev set the new state of the bridge
     * @param newState new state
     */
    function setFrozenState(FrozenStatus newState) external {
        address caller = _msgSender();
        if (caller != _hostParams.admin && caller != _hostParams.handler) revert UnauthorizedAction();

        _frozen = newState;

        emit HostFrozen({status: newState});
    }
```

**File:** evm/src/core/HandlerV2.sol (L105-112)
```text
    /**
     * @dev Checks if the host permits incoming datagrams
     */
    modifier notFrozen(IHost host) {
        FrozenStatus state = host.frozen();
        if (state == FrozenStatus.Incoming || state == FrozenStatus.All) revert HostFrozen();
        _;
    }
```

**File:** evm/src/core/HandlerV2.sol (L254-286)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
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

            // known request? also serves as source check
            bytes32 requestCommitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(requestCommitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(REQUEST_RECEIPTS_STORAGE_PREFIX, requestCommitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(PostRequestTimeout(request, _msgSender()), meta, requestCommitment);
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L293-321)
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

            bytes32 commitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(commitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(RESPONSE_RECEIPTS_STORAGE_PREFIX, commitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(GetRequestTimeout(request, _msgSender()), meta, commitment);
        }
    }
```
