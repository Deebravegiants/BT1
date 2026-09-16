Confirmed — `IntentGatewayV2`/`ExtrinsicIntents.onGetResponse` performs the escrow refund only after a successful `IApp.onGetResponse` callback, and that callback is only reached through `EvmHost.dispatchIncoming(GetResponse,...)`, which unconditionally does `IERC20(feeToken()).safeTransfer(relayer, fee)` immediately afterward, in the same unprotected control flow.

### Title
Unprotected relayer fee transfer in `EvmHost.dispatchIncoming`/`dispatchTimeOut` can revert and permanently block message delivery, freezing escrowed funds - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatchIncoming(GetResponse,...)`, `dispatchTimeOut(GetRequestTimeout,...)` and `dispatchTimeOut(PostRequestTimeout,...)` each execute the destination module's callback behind a low-level `.call` with its own success check (so a module revert is caught and the delivery can be retried), but the subsequent relayer-fee payout `IERC20(feeToken()).safeTransfer(relayer/meta.sender, fee)` is a plain, un-caught external call. If that transfer reverts, the entire transaction reverts, undoing the just-executed, otherwise-successful module callback and its receipt bookkeeping. This is the same bug class as the external report: an unprotected external call late in a delivery/completion path can revert and block the whole operation, forcing a workaround or leaving funds stuck until the revert condition is fixed.

### Finding Description [1](#0-0) 

`dispatchIncoming(GetResponse memory response, address relayer)` calls `IApp.onGetResponse` via low-level `.call`; if it fails, the receipt is deleted and the function returns early so the message can be retried. But once the callback succeeds, the function proceeds to `IERC20(feeToken()).safeTransfer(relayer, fee)` with no try/catch. Any condition that makes this ERC20 transfer revert (fee token pause, relayer blacklist on the fee token, fee token contract bug, or any transfer-restriction logic) reverts the whole `dispatchIncoming` call — reverting the state changes the module callback just made.

The same unprotected pattern exists in the timeout paths: [2](#0-1) 

`dispatchTimeOut(GetRequestTimeout,...)` and `dispatchTimeOut(PostRequestTimeout,...)` both call the module's `onGetTimeout`/`onPostRequestTimeout` behind a guarded `.call`, then unconditionally attempt `IERC20(feeToken()).safeTransfer(meta.sender, meta.fee)` after a successful callback, with no fallback if that transfer fails.

A concrete downstream impact is `IntentGatewayV2`'s cross-chain order-cancellation flow: [3](#0-2) 

`ExtrinsicIntents.onGetResponse` releases the user's escrowed input tokens back to them only when it is reached via a successful `EvmHost.dispatchIncoming(GetResponse,...)` call. If the fee-payout revert described above fires on this exact response, the whole delivery (including the escrow refund the module was about to perform) is rolled back, and it will keep rolling back on every retry as long as the fee-transfer condition persists — since the fee amount, token, and (for the GetResponse path) relayer are all fixed by the already-committed request/response data.

### Impact Explanation
This blocks delivery of the affected response/timeout permanently while the fee-transfer condition holds (e.g., a paused or blacklist-capable fee token), and for `IntentGatewayV2` cancellations this directly freezes the user's escrowed order inputs, since the refund and the (unrelated) fee payment are coupled into one all-or-nothing external call sequence. Unlike `dispatchIncoming(PostRequest,...)`, which is fully guarded and safely returns early on any downstream failure, these three entry points let a fee-accounting side effect hold a successfully-processed application callback hostage.

### Likelihood Explanation
Fee tokens configured for `IHost.feeToken()` are governance-controlled ERC20s (often stablecoins) that commonly implement pausability or address blacklisting; either mechanism, or simply the token contract reverting on any edge case, is sufficient to trigger this path without any special reachability requirement — it fires on the ordinary, permissionless `handleGetResponses`/`handlePostRequestTimeouts`/`handleGetTimeouts` delivery flow that any relayer can invoke.

### Recommendation
Wrap the relayer/refund fee transfer in `dispatchIncoming(GetResponse,...)`, `dispatchTimeOut(GetRequestTimeout,...)`, and `dispatchTimeOut(PostRequestTimeout,...)` in a try/catch (or use a low-level `.call` with a success check), and on failure credit the amount to an internal pull-based balance (e.g., a per-relayer/per-sender claimable mapping) rather than reverting the whole delivery. This decouples the correctness of message/callback delivery from the liveness of the fee token's transfer mechanics, matching the pattern already used for the module callback itself.

### Proof of Concept
1. Fee token `feeToken()` is a governance-settable ERC20 that supports pausing or address blacklisting (a realistic configuration for stablecoin fee tokens).
2. A user places a cross-chain order via `IntentGatewayV2`/`ExtrinsicIntents`, which escrows input tokens and later dispatches a GET request during `_cancelFromSource`.
3. The GET response becomes deliverable; a relayer calls `HandlerV2.handleGetResponses`, which calls `EvmHost.dispatchIncoming(GetResponse,...)`.
4. `IApp.onGetResponse` succeeds internally (the module is ready to refund escrow), but immediately after, `feeToken()` is paused/blacklists the relayer, so `IERC20(feeToken()).safeTransfer(relayer, fee)` reverts.
5. The entire `dispatchIncoming` call reverts, so the escrow refund never lands and the response receipt is never marked delivered.
6. Every subsequent relayer submission of the same proof hits the same fee-token condition (same `relayer`/`fee`/`feeToken` — fixed by the already-existing `_requestCommitments[commitment]`), so the order's escrowed funds remain frozen until the fee token's blacklist/pause state is fixed by its own governance, an entity independent of Hyperbridge.

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

**File:** evm/src/core/EvmHost.sol (L856-906)
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L352-366)
```text
    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```
