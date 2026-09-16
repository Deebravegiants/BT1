## Title
Missing `_requestCommitments` cleanup in `EvmHost.dispatchIncoming(GetResponse)` enables double delivery of `onGetResponse` + `onGetTimeout` for the same GET request - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse, ...)` never deletes the outgoing `_requestCommitments[commitment]` entry after successfully delivering a `GetResponse` to the destination `IApp`, unlike every other terminal state transition (`dispatchTimeOut` for both Post and Get requests explicitly `delete _requestCommitments[commitment]`). This missing cleanup operation leaves the commitment "alive" in storage even though the request has already been resolved, which allows the same GET request to later be processed a second time through the timeout path, delivering both `onGetResponse` and `onGetTimeout` to the destination module for the identical commitment.

### Finding Description
Compare the three terminal handlers in `EvmHost.sol`: [1](#0-0) 

`dispatchIncoming(GetResponse ...)` sets `_responseReceipts[commitment]`, invokes `onGetResponse`, pays the relayer fee out of `_requestCommitments[commitment].fee`, but **never deletes `_requestCommitments[commitment]`**.

Contrast with the timeout path, which explicitly performs this cleanup as "replay protection": [2](#0-1) 

`handleGetRequestTimeouts` in `HandlerV2.sol` only gates dispatch of a GET timeout on: (a) `request.timeout() > state.timestamp` is false, (b) `_requestCommitments[commitment]` still known (`meta.sender != address(0)`), and (c) a non-membership proof, verified against a **historical** `StateMachineHeight` state root stored on the coprocessor, that no response receipt existed there: [3](#0-2) 

Because `EvmHost` retains state-machine commitments for every previously-committed height (`_stateCommitments[stateMachineId][height]`) rather than pruning them, an attacker/relayer can supply a non-membership proof from a state height that predates the moment the coprocessor recorded the response (`pallet_ismp::Responded`) — a window that legitimately exists whenever the GET request already timed out but the response is delivered after the timeout (a normal, expected race given asynchronous relaying and challenge periods). Since `dispatchTimeOut` for `GetRequestTimeout` never checks the EVM host's own `_responseReceipts[commitment]`, and `_requestCommitments[commitment]` was never deleted by the earlier successful `dispatchIncoming(GetResponse)` call, the timeout call passes the `UnknownMessage` guard in `handleGetRequestTimeouts` and successfully dispatches `onGetTimeout` for a request whose `onGetResponse` has already been executed.

### Impact Explanation
This produces a forged/duplicate message delivery: the destination `IApp` module receives both a successful response callback and a timeout callback for the same GET request. Any `IApp` that performs state changes (e.g., releasing escrowed funds, minting, marking an intent fulfilled) on `onGetResponse` and a compensating rollback/refund on `onGetTimeout` (as the documented and recommended pattern instructs) can be driven into an inconsistent double-spend state — e.g., funds released on success and again refunded/re-released on the subsequent forged timeout — a concrete theft/double-payment scenario reachable by any relayer submitting a permissionless `handleGetRequestTimeouts` call. This satisfies the "forged message delivery" / "unauthorized app action" criteria.

### Likelihood Explanation
Reachable via two permissionless dispatcher calls (`handleGetResponses` then `handleGetRequestTimeouts`) that any relayer can submit; it only requires ordinary state commitments already retained by the host and does not require any privileged role, malicious admin, or governance. The precondition — a response delivered after the request's `timeout_timestamp` has elapsed, with an earlier state-machine height available whose trie predates the coprocessor's `Responded` flag — is a normal occurrence rather than a contrived edge case, since GET requests intentionally support post-timeout responses and relayers race for the response fee.

### Recommendation
Add `delete _requestCommitments[commitment];` in `dispatchIncoming(GetResponse ...)` immediately upon successful `onGetResponse` delivery (mirroring the `dispatchTimeOut` cleanup), and/or have `dispatchTimeOut(GetRequestTimeout ...)` reject dispatch when `_responseReceipts[commitment]` is already set, so a request that already received a response can never subsequently be timed out.

### Proof of Concept
1. Source chain dispatches a `GetRequest` with `timeout_timestamp = T`; `_requestCommitments[commitment]` is stored with fee metadata.
2. State machine height `H1` (timestamp `t1 < T`) is committed on `EvmHost`; at this height the coprocessor has not yet recorded `Responded` for `commitment` (response not yet produced).
3. Time passes; `T` elapses (request "timed out" on-chain conceptually), but no timeout message has been submitted yet.
4. A relayer submits `handleGetResponses` with a valid membership proof; `EvmHost.dispatchIncoming(GetResponse ...)` runs, successfully calls `onGetResponse`, pays the fee, but leaves `_requestCommitments[commitment]` intact.
5. An attacker (or the same/another relayer) submits `handleGetRequestTimeouts` referencing the earlier height `H1` (still stored in `_stateCommitments`), with `H1.timestamp > T` satisfied by choosing/awaiting a height where `state.timestamp > T` but the non-membership proof for `RESPONSE_RECEIPTS_STORAGE_PREFIX + commitment` at that height's trie still succeeds (any height committed before the coprocessor recorded the response).
6. `handleGetRequestTimeouts` finds `meta.sender != address(0)` (commitment never deleted) and the non-membership proof passes, so `host.dispatchTimeOut(GetRequestTimeout, meta, commitment)` executes, invoking `onGetTimeout` on the destination module even though `onGetResponse` was already delivered for the same commitment in step 4. [4](#0-3) [2](#0-1) [5](#0-4)

### Citations

**File:** evm/src/core/EvmHost.sol (L820-847)
```text
    /**
     * @dev Dispatch an incoming GET response to source module
     * @param response - get response
     */
    function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
        // replay protection
        bytes32 commitment = response.request.hash();
        _responseReceipts[commitment] = ResponseReceipt({
            relayer: relayer,
            responseCommitment: response.hash()
        });

        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

        if (!success) {
            // so that it can be retried
            delete _responseReceipts[commitment];
            return;
        }

        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L856-877)
```text
    function dispatchTimeOut(
        GetRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/HandlerV2.sol (L288-321)
```text
    /**
     * @dev Check the provided Get request timeouts, then dispatch to modules
     * @param host - Ismp host
     * @param message - batch get request timeouts
     */
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
