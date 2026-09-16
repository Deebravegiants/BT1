### Title
Global `FrozenStatus.All`/`Incoming` freeze blocks timeout processing, permanently locking in-flight request funds with no graceful settlement path - (File: `evm/src/core/HandlerV2.sol`, `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost` only exposes a single, blunt kill-switch — `FrozenStatus` (`None`/`Incoming`/`Outgoing`/`All`) — to react to a malfunctioning or compromised consensus client, exactly analogous to `setSymbolValidationState` in the referenced report. There is no intermediate "settle pending, reject new" state. Critically, the `notFrozen(host)` modifier that guards `handlePostRequestTimeouts`/`handleGetRequestTimeouts` also reverts when the host is frozen with `Incoming` or `All`, meaning that the one mechanism available to release funds already committed for in-flight requests (timeout + refund) is itself disabled by the same freeze that an admin would apply to stop a malfunctioning consensus client.

### Finding Description
`EvmHost.dispatch()` is guarded by `notFrozen()` which blocks new outgoing dispatch on `Outgoing`/`All`: [1](#0-0) 

`HandlerV2` defines its own `notFrozen(host)` modifier which blocks processing when `Incoming` or `All`: [2](#0-1) 

This same modifier gates `handleConsensus` (so no new consensus/state updates can land while frozen with `Incoming`/`All`): [3](#0-2) 

And it also gates `handlePostRequestTimeouts` and `handleGetRequestTimeouts`, the only functions that trigger `onPostRequestTimeout`/`onGetTimeout` callbacks and the associated relayer-fee refund: [4](#0-3) [5](#0-4) 

The refund/callback path itself lives in `EvmHost.dispatchTimeOut`, called only from these gated handler functions: [6](#0-5) 

So when the admin freezes the host to `Incoming` or `All` — the natural, and only, response to a malfunctioning/compromised consensus client (the price-oracle analog) — it simultaneously:
1. Disallows delivering new consensus updates (`handleConsensus` reverts), so no new `StateCommitment`s can be produced.
2. Disallows processing POST/GET timeouts (`handlePostRequestTimeouts`/`handleGetRequestTimeouts` revert), which is the only path back to `dispatchTimeOut` → module timeout callback → relayer-fee refund.

Any request dispatched before the freeze (fee already escrowed in `_requestCommitments`, and any principal already locked in a downstream `IApp` such as a token-bridge module awaiting `onPostRequestTimeout`) has no way to be gracefully settled: it can't be delivered (frozen), and it can't be timed out/refunded either (also frozen). There is no separate status such as "close-only"/"settle" that would still allow already-pending in-flight messages to resolve (via timeout) while blocking new dispatches — exactly the missing capability flagged in the referenced report for `ControlFacet.setSymbolValidationState`.

### Impact Explanation
Once the host is frozen with `Incoming` or `All` (the response to a detected consensus fault/misbehaving oracle-equivalent), all pending cross-chain messages dispatched prior to the freeze become stuck indefinitely:
- Relayer fees held in `_requestCommitments[commitment].fee` cannot be refunded via timeout, since `dispatchTimeOut` is unreachable.
- Any principal value escrowed by downstream `IApp` contracts (e.g. token-bridging apps) awaiting `onPostRequestTimeout`/`onGetTimeout` to trigger a refund remains locked for as long as the freeze persists — which, for a genuine consensus fault, may be indefinite, since unfreezing without fixing the underlying fault would re-expose the same risk that justified freezing in the first place.
This is a direct funds-locking impact matching "Medium" severity in the referenced report: no graceful settlement mechanism exists, only a blunt pause that also disables the pending-message recovery path.

### Likelihood Explanation
This is triggered by the intended admin/governance action of freezing the host in response to a consensus fault — not by an attacker, but the vulnerability is that the protocol's own designed incident-response mechanism creates the fund-lock. Any time governance needs to react defensively to a compromised or malfunctioning consensus client (a realistic and anticipated event, as evidenced by the existence of `freeze_client`/fraud-proof mechanisms elsewhere in the protocol), applying the available `FrozenStatus.Incoming`/`All` will simultaneously strand all in-flight requests with no recovery path until the freeze is lifted.

### Recommendation
Decouple "block new incoming/outgoing dispatch" from "block timeout/refund processing". Specifically:
- Do not gate `handlePostRequestTimeouts`/`handleGetRequestTimeouts` (and the corresponding `dispatchTimeOut`) behind the same `notFrozen` check used for message delivery and consensus updates, or introduce a distinct `FrozenStatus` (e.g. a "SettleOnly"/"CloseOnly" state) that still permits non-membership timeout proofs and refunds while blocking new dispatch and new consensus-derived deliveries.
- Alternatively, allow timeouts to be provable against previously-stored (pre-freeze) state commitments/timestamps without requiring new consensus updates, so pending requests can still resolve via timeout even while the host is fully frozen against new deliveries.

### Proof of Concept
1. User calls `EvmHost.dispatch()` with a `DispatchPost`, escrowing a relayer fee (and, via a downstream `IApp` like a token bridge, escrowing principal) — commitment stored in `_requestCommitments`. [7](#0-6) 
2. Admin detects a consensus fault/misbehaving state and calls `setFrozenState(FrozenStatus.All)` (or `Incoming`) to stop the protocol from processing further messages — the only tool available, analogous to `setSymbolValidationState(invalid)`.
3. The request's `timeout_timestamp` elapses. A relayer attempts `HandlerV2.handlePostRequestTimeouts(host, message)` to trigger the refund.
4. The call reverts with `HostFrozen()` because `notFrozen(host)` sees `FrozenStatus.All`: [2](#0-1) 
5. The fee (and any escrowed principal in the downstream app) remains locked in the host/app contracts for as long as the freeze persists, with no alternate settlement path.

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

**File:** evm/src/core/EvmHost.sol (L879-906)
```text
    /**
     * @dev Dispatch an incoming POST timeout to the source module
     * @param timeout - timed-out post request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
    function dispatchTimeOut(
        PostRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit PostRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/EvmHost.sol (L921-930)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
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

**File:** evm/src/core/HandlerV2.sol (L144-150)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);
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
