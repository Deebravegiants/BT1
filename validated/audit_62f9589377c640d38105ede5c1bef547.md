### Title
EvmHost fails to clear `_requestCommitments` after a GET response is delivered, allowing the escrowed request fee to be paid out twice — ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming(GetResponse memory response, address relayer)` records a `_responseReceipts` entry for replay protection and pays the relayer its reward from `_requestCommitments[commitment].fee`, but it never deletes `_requestCommitments[commitment]` itself. [1](#0-0)  Every sibling delete path in the same contract (`dispatchTimeOut` for both GET and POST requests) explicitly clears `_requestCommitments[commitment]` as its replay-protection step. [2](#0-1)  Because the GET-response path is the one exception, the exact same escrowed `FeeMetadata` (sender + fee) that was already consumed to reward the relayer remains fully intact and later re-readable by `HandlerV2.handleGetRequestTimeouts`, which uses it to authorize a second payout. [3](#0-2) 

### Finding Description
This mirrors the CVE-2022-50880 bug class: a shared resource (there, `ath10k_peer`; here, the escrowed `FeeMetadata` for a request commitment) is reachable through two independent code paths keyed off the same identifier, but only one of the two "delete" paths actually clears the underlying state. The other path continues to observe and act on the stale entry as if it were still valid, producing a second, illegitimate consumption of the resource.

Concretely:
1. A GET request is dispatched and its fee is escrowed in `_requestCommitments[commitment]`.
2. The response is delivered via `HandlerV2.handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse, relayer)`. This sets `_responseReceipts[commitment]` (so the handler-level duplicate check on `responseReceipts(...).relayer` blocks resubmitting the *same* response leaf) and pays `_requestCommitments[commitment].fee` to the relayer — but leaves `_requestCommitments[commitment]` populated. [1](#0-0) 
3. Because `_requestCommitments[commitment]` is untouched, `meta.sender != address(0)` still holds, so the request is still considered "known" by `HandlerV2.handleGetRequestTimeouts`, which reads `meta = host.requestCommitments(commitment)` and, given a valid state non-membership proof for the response-receipt key on the configured state height, calls `host.dispatchTimeOut(GetRequestTimeout(...), meta, commitment)`. [4](#0-3) 
4. `dispatchTimeOut` for GET requests deletes `_requestCommitments[commitment]` (now, for the first time) and, on a successful module callback, refunds `meta.fee` to `meta.sender` — the original fee payer. [2](#0-1) 

The net effect: for one escrowed fee, the host pays it out twice from its fee-token balance — once as a relayer reward on response delivery, and again as a sender refund on the (spurious) timeout — because the request metadata that should have been invalidated on step 2 was never removed.

### Impact Explanation
This is a concrete drain of the host's fee-token reserve: the same escrowed amount is transferred out twice for a single dispatched GET request, at the expense of the pool that backs relayer rewards/refunds for all other pending requests. This satisfies the "concrete theft / unbacked payout" bar — funds leave the contract that were never re-escrowed for the second payout.

### Likelihood Explanation
The path is reachable by any relayer/dispatcher through the standard message-relaying flow (no privileged role required): deliver the GET response through `handleGetResponses`, then submit a non-membership proof through `handleGetRequestTimeouts` for the same commitment. The non-membership proof only needs to be valid against *some* state height that the destination host still accepts (any height at or before the coprocessor recorded the response receipt), which is realistic given `dispatchTimeOut` is callable at any subsequently-verified height and there is no check tying the timeout height to "after the response was delivered."

### Recommendation
In `dispatchIncoming(GetResponse memory response, address relayer)`, delete `_requestCommitments[commitment]` immediately after (or instead of merely reading) the fee payout, mirroring the pattern used in `dispatchTimeOut`. If retry-on-failure semantics are required (as with the POST/timeout paths), restore the metadata only when the module callback fails, exactly as done in `dispatchTimeOut`.

### Proof of Concept
1. Dispatch a `GetRequest` with a non-zero `fee`; `_requestCommitments[commitment]` is populated with `{sender, fee}`.
2. Relayer A submits `handleGetResponses` with a valid `GetResponseLeaf` for the request; `EvmHost.dispatchIncoming(GetResponse, relayerA)` succeeds, `_responseReceipts[commitment]` is set, and `fee` is transferred to `relayerA`. `_requestCommitments[commitment]` is untouched (still `{sender, fee}`).
3. Any actor (or relayer A again) later submits `handleGetRequestTimeouts` for the same `commitment` with a state height/non-membership proof that the response receipt is absent at that height (e.g., an earlier finalized height than the one the response was actually recorded at, or a height on a state machine the coprocessor never updates with the response record for this particular route).
4. `handleGetRequestTimeouts` reads `meta = host.requestCommitments(commitment)` (still populated), passes the non-membership check, and calls `host.dispatchTimeOut(GetRequestTimeout(request, msgSender), meta, commitment)`.
5. `dispatchTimeOut` deletes `_requestCommitments[commitment]`, invokes `onGetTimeout` on the origin module, and on success transfers `meta.fee` to `meta.sender` — a second payout of the same escrowed fee.

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
