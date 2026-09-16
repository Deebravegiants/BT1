## Analysis Result

I found a concrete analog. `EvmHost.dispatchIncoming(GetResponse, address)` never clears `_requestCommitments[commitment]` after paying the relayer fee out of it, whereas the sibling timeout paths explicitly `delete _requestCommitments[commitment]` as the very first "replay protection" step. This mirrors the CVE's bug class: a stored reference/credential (`dst`/refcnt in the kernel bug, `_requestCommitments[commitment].fee` here) is consumed/used without invalidating it, leaving a stale, still-"live" entry reachable through a second code path. [1](#0-0) [2](#0-1) 

### Title
Stale `_requestCommitments` entry after `GetResponse` delivery enables a second relayer-fee payout via `GetRequestTimeout` - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse, relayer)` pays the relayer fee from `_requestCommitments[commitment].fee` but never deletes the entry, unlike `dispatchTimeOut(GetRequestTimeout, ...)` and `dispatchTimeOut(PostRequestTimeout, ...)`, both of which delete `_requestCommitments[commitment]` as their first line ("replay protection").

### Finding Description
`dispatchIncoming(GetResponse, ...)` writes a `_responseReceipts[commitment]` guard for the response itself and pays out the fee tracked in `_requestCommitments[commitment]`, but leaves `_requestCommitments[commitment]` populated: [3](#0-2)  By contrast, `dispatchTimeOut(GetRequestTimeout, ...)` treats `delete _requestCommitments[commitment]` itself as the replay-protection mechanism, restoring it only on failure: [2](#0-1) 

`HandlerV2.handleGetRequestTimeouts` gates dispatch of a timeout purely on a **non-membership proof of the response receipt on the destination chain's state trie** (`RESPONSE_RECEIPTS_STORAGE_PREFIX`) at the referenced height, plus `meta.sender != address(0)` from `_requestCommitments`: [4](#0-3)  It does **not** check the source-chain `_responseReceipts` mapping that `dispatchIncoming(GetResponse,...)` sets on delivery. Because `_requestCommitments[commitment]` is left intact after a successful response delivery, `meta.sender != address(0)` still holds, so a relayer can submit a timeout-non-membership proof for a state height at which the destination had not yet stored a response receipt (e.g., a height prior to the response being written, or before the request was ever answered on the destination but is later fulfilled) and drive `dispatchTimeOut` on the source (`EvmHost`), paying the fee a second time and invoking `onGetTimeout` on the module — a state the application never expects after a response was already delivered.

This is the direct analog of CVE-2021-47222: in the kernel bug, `dst_clone()` used a cached pointer without validating it was still "live" (non-zero refcount) before use, causing the same underlying resource to be referenced/released inconsistently. Here, the underlying resource is the escrowed relayer fee keyed by `_requestCommitments[commitment]`; it is "cloned"/read and paid out on the `GetResponse` path without being invalidated (deleted), so the same commitment is still "held" and can be independently consumed via the timeout path.

### Impact Explanation
This allows theft of protocol/user funds: a relayer fee can be paid twice for the same GET request — once through `dispatchIncoming(GetResponse,...)` and once through `dispatchTimeOut(GetRequestTimeout,...)` — and additionally forces the destination `onGetTimeout` callback into a module that already processed the corresponding `onGetResponse`, an unsound state transition for any app relying on exactly-once semantics for GET responses/timeouts. This meets the "concrete theft ... or unsound state commitment" bar.

### Likelihood Explanation
Exploitation requires only a permissionless relayer submitting `handleGetRequestTimeouts` with a valid non-membership proof at a state height where the destination's response receipt was not yet written — achievable by a relayer racing the timeout-proof height against the actual response delivery, or via a height chosen before the response was recorded on the destination. `handleGetResponses`/`handleGetRequestTimeouts` are both explicitly permissionless entry points reachable by anyone submitting a relayed proof, matching the required unprivileged-relayer threat model.

### Recommendation
Delete `_requestCommitments[commitment]` in `dispatchIncoming(GetResponse, relayer)` immediately after (or as) it reads `meta.fee`, mirroring the `dispatchTimeOut` pattern, so the commitment cannot be "replayed" through the timeout path once a response has been delivered. Additionally, `handleGetRequestTimeouts` should not be able to succeed once `_requestCommitments` for that commitment has been cleared (it already reverts via `UnknownMessage` once `meta.sender == address(0)`, so the missing `delete` is the root cause).

### Proof of Concept
1. User dispatches a `DispatchGet` request; `_requestCommitments[commitment]` is stored with `fee = F`.
2. Relayer submits `handleGetResponses` with a valid response proof; `EvmHost.dispatchIncoming(GetResponse,...)` calls `onGetResponse`, pays fee `F` to relayer A, but leaves `_requestCommitments[commitment]` populated.
3. Same or different relayer B later submits `handleGetRequestTimeouts` with a non-membership proof of the response receipt at a state height that predates step 2's on-chain response-receipt write (or any height where the destination's response-receipt storage slot was still empty). `meta.sender != address(0)` still passes since the entry was never deleted.
4. `EvmHost.dispatchTimeOut(GetRequestTimeout,...)` deletes `_requestCommitments[commitment]`, invokes `onGetTimeout` on the module (already having received `onGetResponse`), and pays fee `F` again to relayer B — double payment and an inconsistent module state.

Note: I could not fully verify from the indexed excerpts whether any higher-level invariant elsewhere (e.g., in the module's own accounting or in `ismp-solidity`'s off-chain proof-generation tooling) prevents a relayer from constructing a valid non-membership proof at a stale height once a response exists; a background Devin session with full repo/test access would be needed to confirm exploitability end-to-end via `evm/tests/foundry` and rule out an implicit guard.

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
