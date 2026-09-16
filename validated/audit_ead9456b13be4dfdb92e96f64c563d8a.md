### Title
Double-Payment of GET Request Escrowed Fee via Stale `_requestCommitments` Entry — (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` pays the escrowed relayer fee out of `_requestCommitments[commitment]` on a successful `onGetResponse` callback, but never deletes or otherwise invalidates that entry. Because the entry survives a successful delivery, an attacker can subsequently submit a `GetRequestTimeout` for the same commitment — using a non-membership proof anchored at an *older*, already-finalized destination-chain height (from before the response existed) — and cause `dispatchTimeOut(GetRequestTimeout, ...)` to pay the same escrowed fee out a second time. This is the same bug class as CVE-2026-66032 (libssh2 `sftp_open`): a resource is released (freed / paid out) on the success path without clearing the state that guards it, so a later error/alternate path performs the release again on the same resource.

### Finding Description
Relevant code, `evm/src/core/EvmHost.sol`: [1](#0-0) 

`dispatchIncoming(GetResponse memory response, address relayer)` reads `_requestCommitments[commitment].fee`, transfers it to `relayer` on success, but does **not** `delete _requestCommitments[commitment]` in either the success or failure branch.

Compare with `dispatchTimeOut(GetRequestTimeout, ...)`: [2](#0-1) 

This function is guarded only by `meta.sender == address(0)` (i.e., "does a commitment still exist") in `HandlerV2.handleGetRequestTimeouts`: [3](#0-2) 

The only replay protection for the timeout path is a **non-membership proof of a `ResponseReceipt`** in the *destination* chain's state trie at a chosen, already-finalized `message.height`. Because Hyperbridge/pallet-ismp state commitments are stored per-height and are not deleted, an attacker can pick any earlier height `H1` where:
1. `state.timestamp(H1) >= request.timeout()` (so the "timed out?" check passes), and
2. the destination chain had not yet recorded a `ResponseReceipt` for this GET request at `H1` (so the non-membership proof against `RESPONSE_RECEIPTS_STORAGE_PREFIX` succeeds),

even though the response was legitimately produced and delivered to the source chain later (at a subsequent height `H2 > H1`). Since `_requestCommitments[commitment]` was never cleared by the earlier successful `dispatchIncoming(GetResponse, ...)` call, `meta.sender != address(0)` still holds, so `handleGetRequestTimeouts` accepts the stale-height proof and calls `host.dispatchTimeOut(...)`, which pays `meta.fee` to `meta.sender` a second time — on top of the fee already paid to the relayer at delivery.

This mirrors the libssh2 root cause precisely: the success path ("free"/pay-out on `SSH_FXP_STATUS`/`onGetResponse` success) does not null out the shared handle (`_requestCommitments[commitment]`), so a later, distinct error path (`sftp_packet_require` error / `GetRequestTimeout` non-membership branch) performs a second release on the same resource, corrupting shared state (heap / escrowed ERC20 balance).

### Impact Explanation
This allows theft of the `feeToken` (e.g., DAI) balance held by `EvmHost`: every GET request fee can be extracted twice — once as the legitimate relayer reward via `dispatchIncoming`, and a second time as a "timeout refund" via `dispatchTimeOut(GetRequestTimeout, ...)`, both payable to attacker-controlled addresses (the caller supplies `_msgSender()` as relayer in the first call, and `meta.sender`/payer is whoever originally dispatched the GET, but an attacker acting as both requester and relayer captures both payouts). This is concrete theft of funds from the host contract, reachable by any permissionless relayer submitting a single relayed proof — squarely in scope (`HandlerV2`/`EvmHost` dispatch, no privileged actor required).

### Likelihood Explanation
Both `handlePostRequests`/`handleGetResponses` and `handleGetRequestTimeouts` are explicitly permissionless (`external`, no access control beyond `notFrozen`). The only obstacle is having, at the time of the attack, an already-stored destination state commitment at a height whose recorded timestamp exceeds the request's timeout but predates the response being recorded — this is a routine occurrence given normal block production and the protocol's own multi-height commitment retention (commitments are never pruned proactively; `deleteStateMachineCommitment` exists only for fisherman-flagged invalid states). No consensus forgery or governance compromise is required, only ordinary use of already-verified state commitments.

### Recommendation
Delete (or otherwise invalidate, e.g. zero out) `_requestCommitments[commitment]` inside `dispatchIncoming(GetResponse, ...)` immediately upon successful delivery (mirroring the pattern already used for `_requestReceipts`/`_responseReceipts` replay protection), so that a later `dispatchTimeOut(GetRequestTimeout, ...)` for the same commitment always fails the `meta.sender == address(0)` check regardless of which destination-chain height's proof is presented.

### Proof of Concept
1. Attacker dispatches a `GetRequest` from the EVM host with fee `F`, `payer = attacker`.
2. Hyperbridge routes the request to the destination chain; before the destination processes it, the destination chain finalizes a state commitment at height `H1` (no `ResponseReceipt` present yet), with `timestamp(H1) >= request.timeout()`.
3. Destination later processes the GET and Hyperbridge relays the resulting `GetResponse` back to the EVM host. Attacker (or a colluding relayer) calls `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse, attackerRelayer)`. `onGetResponse` succeeds, fee `F` is transferred to `attackerRelayer`; `_requestCommitments[commitment]` is **not** cleared (per `evm/src/core/EvmHost.sol` lines 824-847).
4. Attacker calls `HandlerV2.handleGetRequestTimeouts` with `message.height = H1` and the non-membership proof from step 2 (`RESPONSE_RECEIPTS_STORAGE_PREFIX ++ commitment` absent at `H1`).
5. `meta = host.requestCommitments(commitment)` is still non-zero, non-membership proof at `H1` verifies, `dispatchTimeOut(GetRequestTimeout, ...)` runs; `onGetTimeout` on the app is expected to succeed (idempotent apps are explicitly required by protocol docs to tolerate repeated timeout calls), and fee `F` is transferred a second time to `meta.sender` (attacker).
6. Net result: attacker receives `2F` in `feeToken` for a single `F`-fee GET request — funds drained from `EvmHost`. [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** evm/src/core/EvmHost.sol (L849-877)
```text
    /**
     * @dev Dispatch an incoming GET timeout to the source module.
     * @notice Does not refund any protocol fees.
     * @param timeout - timed-out get request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
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
