### Title
Missing contract-existence check on return-path low-level calls causes GET responses/timeouts to be marked handled without executing app callbacks - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming(GetResponse, ...)`, `dispatchTimeOut(GetRequestTimeout, ...)`, and `dispatchTimeOut(PostRequestTimeout, ...)` deliver a message to the originating app by low-level `.call()` on an address decoded from the message (`response.request.from` / `timeout.request.from`) without first checking that the address has code, unlike the sibling function `dispatchIncoming(PostRequest, ...)` which explicitly performs an `extcodesize` check before calling. Per Solidity's documented EVM semantics, a low-level `call()` to an address with no code returns `success = true` trivially. Because these three functions treat that trivial success identically to a real, successful app callback, they permanently mark the message as delivered (deleting replay-protection state and, for `GetResponse`, paying out the relayer fee) even though the app's `onGetResponse`/`onGetTimeout`/`onPostRequestTimeout` logic never executed.

### Finding Description
In `evm/src/core/EvmHost.sol`:

- `dispatchIncoming(PostRequest memory request, address relayer)` (lines 794-818) correctly guards against the "call to non-existent code" pitfall: [1](#0-0) 
It computes `extcodesize(destination)` and, if zero, returns early **without** writing `_requestReceipts[commitment]`, allowing the message to be retried later once/if the destination contract exists.

- `dispatchIncoming(GetResponse memory response, address relayer)` (lines 820-847) has no such guard: [2](#0-1) 
It unconditionally writes `_responseReceipts[commitment]` *before* calling, then calls `_bytesToAddress(response.request.from).call(...)`. If that address has no code, the call trivially returns `success = true`, so the function proceeds to emit `GetRequestHandled` and pay the relayer fee via `IERC20(feeToken()).safeTransfer(relayer, fee)` — even though `onGetResponse` never ran.

- `dispatchTimeOut(GetRequestTimeout ...)` (lines 856-877) and `dispatchTimeOut(PostRequestTimeout ...)` (lines 885-900) have the same pattern: [3](#0-2) 
`_requestCommitments[commitment]` is deleted up front, then `_bytesToAddress(timeout.request.from).call(...)` is invoked. A no-code target trivially "succeeds", so the timeout callback (`onGetTimeout`/`onPostRequestTimeout`) that apps rely on to unwind escrowed state (e.g., refund logic in `IntentGatewayV2`/`HyperFungibleToken`-style apps) silently never fires, yet the commitment is already deleted and the fee already refunded to `meta.sender`.

The `from` field of a GET/POST request is set to `msg.sender` of whichever account called `IDispatcher.dispatch(...)` originally — this is not restricted to contracts, and can also become code-less later (e.g., a CREATE2 counterfactual address not yet deployed at delivery time, or a contract that self-destructed). Any unprivileged dispatcher that supplies such an address, intentionally or through normal CREATE2/deployment timing, causes the return-path delivery to be silently treated as fully handled.

### Impact Explanation
Because these three code paths conflate "no-code target" with "successful callback execution," they permanently:
1. Delete the replay-protection/commitment state for the message (no retry path exists, in contrast to the guarded `dispatchIncoming(PostRequest,...)`), and
2. Release protocol funds — relayer fee payout in `dispatchIncoming(GetResponse,...)`, and relayer-fee refund to `meta.sender` in the two `dispatchTimeOut` functions —

without the destination app's callback ever running. Any application whose escrow/refund/settlement logic lives inside `onGetResponse`, `onGetTimeout`, or `onPostRequestTimeout` (e.g., cross-chain intent settlement, GET-based cancellation flows described in `ExtrinsicIntents.sol`) can have its state left inconsistent: the Hyperbridge-side bookkeeping says "handled/refunded" while the app-side escrow was never released, permanently freezing user funds with no mechanism to redeliver the message. This is a Medium/High severity freezing-of-funds and unsound-message-delivery issue, directly analogous to the referenced report's "low-level call silently returns true for non-existent accounts" bug class, but manifesting here as forged delivery/settlement acknowledgment rather than a failed value transfer.

### Likelihood Explanation
Reachable without any privileged role: any account (EOA or contract) can call `IDispatcher.dispatch(DispatchGet)`/`dispatch(DispatchPost)` and become the recorded `from`. CREATE2-based apps that dispatch requests before their counterfactual address is deployed, or apps that are later destroyed/upgraded away, are common real-world patterns. A relayer only needs to submit a valid proof for the response/timeout on the affected commitment — no admin/governance action or malicious insider is required.

### Recommendation
Add the same `extcodesize`/existence check used in `dispatchIncoming(PostRequest,...)` to `dispatchIncoming(GetResponse,...)`, `dispatchTimeOut(GetRequestTimeout,...)`, and `dispatchTimeOut(PostRequestTimeout,...)`: verify the decoded `from` address has code before issuing the low-level `call()`, and if it does not, return early without deleting/writing the commitment/receipt state (mirroring the retry-friendly behavior of the POST-accept path) instead of treating the trivial `success=true` as a genuine callback execution.

### Proof of Concept
1. Dispatch a `DispatchGet` (or `DispatchPost`) request from an address `A` that either is a pure EOA, or a CREATE2 address that is not yet deployed, recording `from = A` in the request.
2. Let the request time out (or receive a GET response) such that a relayer submits the corresponding proof to `EvmHost`.
3. `dispatchTimeOut`/`dispatchIncoming(GetResponse,...)` decodes `A` and calls `A.call(abi.encodeWithSelector(...))`; since `A` has no code, this returns `success = true` trivially.
4. The function proceeds as if the app's callback executed successfully: `_requestCommitments`/`_responseReceipts` state is deleted/finalized and the relayer fee is paid out/refunded, while no `onGetTimeout`/`onGetResponse`/`onPostRequestTimeout` logic ever ran and no retry is possible — compare this to `dispatchIncoming(PostRequest,...)`, which would have returned early instead, preserving the ability to retry once `A` obtains code.

### Citations

**File:** evm/src/core/EvmHost.sol (L794-817)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
```

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
