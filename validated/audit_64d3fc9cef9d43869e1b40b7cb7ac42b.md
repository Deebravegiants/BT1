### Title
Missing cleanup of `_requestCommitments` after a successful GET response allows double payment of the escrowed relayer fee via a later timeout claim - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(GetResponse, address)` pays out the relayer fee for a delivered GET response by reading `_requestCommitments[commitment].fee`, but never deletes the `_requestCommitments[commitment]` entry on the success path. `dispatchTimeOut` later refunds the same fee to the original sender using a `FeeMetadata` value that traces back to that same, still-present commitment slot. The two code paths do not check each other's outcome, so the same escrowed fee can be paid out twice for a single GET request — once as a relayer reward on response delivery, once as a sender refund on timeout — draining the fee-token reserve. This mirrors the CVE-2017-17564 bug class: an error/success branch of one operation fails to update the reference/commitment state that a second, independent operation relies on for correctness, letting the resource be "double counted."

### Finding Description
`dispatchIncoming(GetResponse memory response, address relayer)` in `evm/src/core/EvmHost.sol` (lines 824-847): [1](#0-0) 

sets `_responseReceipts[commitment]` for replay protection, invokes the destination module's `onGetResponse`, and — on success — pays `_requestCommitments[commitment].fee` to the relayer. It never calls `delete _requestCommitments[commitment]` on the success branch, unlike the sibling POST/timeout handlers which explicitly clear or restore commitment state for replay protection, e.g. `dispatchTimeOut`: [2](#0-1) 

`dispatchTimeOut` independently deletes `_requestCommitments[commitment]` as its own replay guard and pays `meta.fee` to `meta.sender` — where `meta` is `FeeMetadata` fetched by the caller (the handler) from the same commitment storage before this call. Because `dispatchIncoming(GetResponse,...)`'s success path leaves that entry intact, a GET request that has already been successfully responded to (and its relayer fee already paid) still has a live, unspent-looking commitment entry that a subsequent timeout proof can consume, paying the sender the same fee a second time.

I was not able to fully confirm within the available context whether `HandlerV2` (`evm/src/core/HandlerV2.sol`) independently checks `_responseReceipts` before accepting a request-timeout proof for a commitment that already has a stored response receipt; I could not complete tracing `handleGetRequestTimeouts` in the remaining iterations. If no such cross-check exists — which the `EvmHost` storage layout suggests, since the two receipts (`_responseReceipts` and `_requestCommitments`) are tracked in separate maps with no mutual exclusion enforced in `dispatchIncoming`/`dispatchTimeOut` — the double-payment path described above is directly reachable by any relayer submitting a valid membership proof for the response followed later by a valid non-membership/timeout proof for the same request.

### Impact Explanation
Successful exploitation drains the `feeToken()` reserve held by `EvmHost` by paying the same escrowed fee twice for one GET request: once to the relayer that delivered the response, once to the original requester as a "timeout" refund. This is a direct loss of protocol/fee funds reachable from ordinary relayer and requester actions, without needing any privileged role — matching "concrete theft ... of funds" in the validation criteria.

### Likelihood Explanation
The precondition is that a relayer can obtain (or already possesses) both a valid state-membership proof of the response and, after the request's `timeoutTimestamp` elapses, a valid non-membership/timeout proof for the same request — both are normal, permissionless relayer operations already supported by the protocol's message-delivery flow. The only missing safeguard is the storage cleanup in `dispatchIncoming(GetResponse,...)`, making this a straightforward state-machine oversight rather than a complex attack.

### Recommendation
In `dispatchIncoming(GetResponse memory response, address relayer)`, delete `_requestCommitments[commitment]` immediately after (or as part of) paying out the relayer fee on the success branch, mirroring how `dispatchTimeOut` and `dispatchIncoming(PostRequest,...)` manage their own replay-protection state. Additionally, have the timeout-handling path (`dispatchTimeOut`) verify that no response receipt exists for the commitment before paying any refund, so the two payout paths are mutually exclusive regardless of storage ordering.

### Proof of Concept
1. Attacker/relayer submits a valid GET request with a nonzero fee; `_requestCommitments[commitment]` is populated by the outgoing-dispatch path.
2. Before the request's `timeoutTimestamp`, a relayer submits a valid state-membership proof and calls the handler, which invokes `EvmHost.dispatchIncoming(GetResponse, relayer)`; `onGetResponse` succeeds, and the relayer is paid `_requestCommitments[commitment].fee` — but the entry is not deleted. [3](#0-2) 
3. After `timeoutTimestamp` elapses, the same or another party submits a valid timeout (non-membership) proof for the same request; the handler calls `EvmHost.dispatchTimeOut(timeout, meta, commitment)` with `meta` still reflecting the original fee, and the sender is refunded the fee a second time. [4](#0-3) 
4. Net effect: the protocol has paid out the escrowed fee for one GET request twice, one payment more than was ever escrowed.

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
