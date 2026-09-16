Confirmed: `dispatchIncoming(GetResponse, address)` in `evm/src/core/EvmHost.sol` pays out the relayer fee from `_requestCommitments[commitment].fee` on a successful GET response delivery but **never deletes `_requestCommitments[commitment]`** afterward, unlike every other terminal path in the same contract (`dispatchTimeOut(GetRequestTimeout,...)` and `dispatchTimeOut(PostRequestTimeout,...)` both `delete _requestCommitments[commitment]` up front as "replay protection," and `dispatchIncoming(PostRequest,...)` clears `_requestReceipts` on failure for retry).

### Title
Stale `_requestCommitments` entry after a successful GET response allows the same relayer-fee escrow to be paid out again via `dispatchTimeOut(GetRequestTimeout)` - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` pays the escrowed relayer fee (`_requestCommitments[commitment].fee`) to the relayer on a successful `onGetResponse` delivery, but leaves the `_requestCommitments[commitment]` entry in storage instead of deleting it, unlike the sibling timeout-handling functions in the same contract which all delete this map entry as their "replay protection" step.

### Finding Description
In `evm/src/core/EvmHost.sol`: [1](#0-0) 
`dispatchIncoming(GetResponse memory response, address relayer)` reads `_requestCommitments[commitment].fee`, transfers it to `relayer`, and emits `GetRequestHandled` — but never clears `_requestCommitments[commitment]`.

Compare with the two `dispatchTimeOut` overloads in the same file, which both treat deleting `_requestCommitments[commitment]` as the "replay protection" primitive before invoking the app callback: [2](#0-1) [3](#0-2) 

`HandlerV2.handleGetRequestTimeouts` gates a timeout dispatch purely on `_requestCommitments` still holding a non-zero `meta.sender` and on a non-membership proof of the *response receipt* against Hyperbridge's own (coprocessor) state: [4](#0-3) 

Because `dispatchIncoming(GetResponse,...)` never clears `_requestCommitments[commitment]`, that map entry is still "known" (`meta.sender != address(0)`) after a GET response has already been delivered and its relayer fee paid. This is structurally analogous to the CVE's double-free class: a resource (`meta.fee` in the `FeeMetadata` for that commitment) is released once, but the bookkeeping that should mark the resource as consumed is never cleared, leaving the door open for a second release path (`dispatchTimeOut(GetRequestTimeout,...)`) to act on the same, stale metadata.

Whether this is actually exploitable end-to-end depends on whether Hyperbridge's own state (the child-trie response receipt checked by the non-membership proof in `handleGetRequestTimeouts`) can, in any circumstance, fail to reflect that a response was already produced for a given request while `_requestCommitments` on the *destination* EVM host is stale. I could not fully verify from the index whether such a state-divergence window exists (e.g. through commitment-cap eviction, MMR pruning, or coprocessor bandwidth-gate rejection paths that could still allow this EVM host to independently deliver and finalize a response) — this is the piece of root-cause proof I was unable to close out given the available tools.

### Impact Explanation
If the divergence window exists, a relayer could collect the relayer fee twice for the same GET request: once via a legitimate `handleGetResponses` delivery, and a second time via `handleGetRequestTimeouts` → `dispatchTimeOut(GetRequestTimeout,...)`, which unconditionally refunds `meta.fee` from the (never-cleared) `_requestCommitments[commitment]` entry. This is a direct loss of protocol/fee-escrow funds (unbacked payout), matching the CVE's "double free" bug class translated to escrowed-fee accounting.

### Likelihood Explanation
Likelihood is uncertain pending confirmation of the exact conditions under which `handleGetRequestTimeouts`'s non-membership proof against Hyperbridge's response-receipt state could pass for a request this EVM host already answered. Absent that confirmation, this should be treated as a **hardening gap** (missing defense-in-depth clear of `_requestCommitments` on the success path) rather than a proven, directly exploitable double-spend — the coprocessor's own dedup (`response_receipt` check in `handle_get_requests`) is the primary line of defense and appears to independently prevent duplicate response production.

### Recommendation
Delete `_requestCommitments[commitment]` in `EvmHost.dispatchIncoming(GetResponse memory response, address relayer)` immediately after a successful `onGetResponse` callback (mirroring the pattern already used in both `dispatchTimeOut` overloads), so a completed GET response can never again satisfy the "known request" check in `handleGetRequestTimeouts`/`dispatchTimeOut(GetRequestTimeout,...)`.

### Proof of Concept
Not fully constructible from the indexed code alone — it requires demonstrating a concrete case where Hyperbridge's (`pallet-ismp`/`state-coprocessor`) response-receipt state fails to reflect a response that the destination EVM host already processed and paid out for, letting a subsequent timeout proof pass `PolkadotTrie.VerifyProof` non-membership check in `HandlerV2.handleGetRequestTimeouts` (`evm/src/core/HandlerV2.sol:293-321`) and reach `EvmHost.dispatchTimeOut(GetRequestTimeout,...)` (`evm/src/core/EvmHost.sol:856-877`) for the same commitment. A Devin session with repo access should verify this by tracing `handle_get_requests` (`modules/pallets/state-coprocessor/src/impls.rs`) and MMR/receipt-pruning code paths to check whether such a divergence is actually reachable; if not reachable, this downgrades to a code-hygiene/hardening recommendation rather than a live vulnerability.

### Citations

**File:** evm/src/core/EvmHost.sol (L824-847)
```text
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
