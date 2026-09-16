Confirmed: `handlePostRequestTimeouts` and `handleGetRequestTimeouts` in `HandlerV2.sol` are unprivileged, callable by any relayer submitting a valid non-membership proof, and they invoke `EvmHost.dispatchTimeOut` which unconditionally refunds `meta.fee` to `meta.sender` via `safeTransfer` after the `onPostRequestTimeout`/`onGetTimeout` callback succeeds. If `meta.sender` is blacklisted by `feeToken()` (e.g., USDC/USDT-style tokens), that transfer reverts the whole transaction, which also undoes the `delete _requestCommitments[commitment]` — so the timeout can never be finalized and the escrowed fee is permanently stuck.

### Title
Timeout dispatch permanently DOSed and fee frozen when the original sender is blacklisted by feeToken - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchTimeOut` (both the `PostRequestTimeout` and `GetRequestTimeout` overloads) refunds the relayer fee to `meta.sender` with `IERC20(feeToken()).safeTransfer(meta.sender, meta.fee)` after the destination module's timeout callback succeeds. If `feeToken()` is a token with a blacklist/freeze mechanism (e.g., USDC) and `meta.sender` (the original dispatching app/EOA) is on that blacklist, this transfer reverts unconditionally, reverting the entire timeout transaction every time it is retried.

### Finding Description
`dispatchTimeOut` first deletes the request commitment for replay protection, invokes the destination module's `onPostRequestTimeout`/`onGetTimeout` callback, and only after that callback succeeds does it attempt `safeTransfer(meta.sender, meta.fee)`: [1](#0-0) 

Because the fee refund happens unconditionally and after the state deletion, a revert in the transfer (e.g., blacklisted `meta.sender` on a token like USDC) reverts the whole call, including the earlier `delete _requestCommitments[commitment]`. Since the request has already timed out on-chain (verified via the non-membership proof of the request/response receipt in `HandlerV2.handlePostRequestTimeouts`/`handleGetRequestTimeouts`), there is no other code path to clear the commitment or reclaim the fee — every future retry hits the exact same revert: [2](#0-1) [3](#0-2) 

This is directly analogous to the referenced `setManager` DOS: an unconditional token transfer to a potentially-blacklisted address is placed in the critical path of an otherwise-routine state transition, and a reverting transfer blocks the whole operation with no fallback.

### Impact Explanation
The timed-out request can never be finalized: `_requestCommitments[commitment]` is never cleared, and the fee escrowed in `feeToken()` for that request is permanently frozen inside `EvmHost`, unrecoverable by the sender, the relayer, or governance (there is no privileged bypass for this specific commitment/fee). This is a permanent freezing-of-funds condition scoped to any request whose original sender becomes blacklisted by the fee token before its timeout is processed.

### Likelihood Explanation
Reachable by any unprivileged relayer submitting a legitimate timeout proof through `HandlerV2.handlePostRequestTimeouts` / `handleGetRequestTimeouts` — no special privileges required. The triggering condition (sender blacklisted by `feeToken()`, e.g. USDC-style asset) is realistic for any Hyperbridge deployment where the configured fee token supports blacklisting, and can also be self-inflicted by a malicious `meta.sender` who dispatches a request and then gets/puts themselves on the blacklist (or simply is a contract that reverts on receiving tokens) specifically to grief the timeout and lock the fee.

### Recommendation
Decouple the fee refund from the state cleanup: either (1) wrap the `safeTransfer` in a try/catch and, on failure, credit the amount to an internal per-account withdrawable balance (pull-payment pattern) rather than pushing it, or (2) perform the commitment deletion in one transaction/step and let the recipient claim the refund separately via a `withdraw`-style function that isolates the transfer's ability to revert from the protocol's replay/timeout bookkeeping.

### Proof of Concept
1. Configure `feeToken()` to a blacklist-capable token (e.g., a USDC-like mock with a `blacklist(address)` function).
2. Dispatch a `PostRequest` (or `GetRequest`) from `meta.sender` with a non-zero `fee`, paid in `feeToken()`.
3. Blacklist `meta.sender` on the fee token before the request times out.
4. Let the request time out; a relayer submits `handlePostRequestTimeouts`/`handleGetRequestTimeouts` with a valid non-membership proof.
5. `EvmHost.dispatchTimeOut` executes the destination module callback successfully, then calls `IERC20(feeToken()).safeTransfer(meta.sender, meta.fee)`, which reverts because `meta.sender` is blacklisted.
6. The entire transaction reverts, restoring `_requestCommitments[commitment]`; every subsequent retry (by any relayer) fails identically, permanently freezing `meta.fee` and leaving the request forever un-timed-out.

### Citations

**File:** evm/src/core/EvmHost.sol (L885-906)
```text
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
