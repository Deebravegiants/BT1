## Title
Missing contract-existence check in `EvmHost.dispatchIncoming(GetResponse)` and `dispatchTimeOut` lets messages be marked as delivered without executing any callback code - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming(PostRequest, address)` explicitly checks `extcodesize` on the destination before invoking `IApp.onAccept`, and returns early (leaving no receipt) when the destination has no code [1](#0-0) . The three sibling delivery paths — `dispatchIncoming(GetResponse, address)`, `dispatchTimeOut(GetRequestTimeout, ...)`, and `dispatchTimeOut(PostRequestTimeout, ...)` — perform the identical low-level `.call(...)` pattern but omit this check entirely [2](#0-1) [3](#0-2) [4](#0-3) .

### Finding Description
Per Solidity's documented warning (the same one cited in the external report), a low-level `.call()` to an address with no code returns `success = true` even though nothing executed. In `dispatchIncoming(GetResponse, address)`, the response receipt (`_responseReceipts[commitment]`) is written *before* the call, at line 827, and is only rolled back `if (!success)` [5](#0-4) . If `_bytesToAddress(response.request.from)` has no code at delivery time, the call trivially "succeeds", so:
- the receipt is kept, permanently marking the GetResponse as delivered (blocking any future retry), and
- the relayer is paid the fee from `_requestCommitments[commitment].fee` as if the callback ran [6](#0-5) .

The same pattern repeats in both `dispatchTimeOut` overloads: the request commitment is deleted (replay protection consumed) before the call, and the relayer/sender fee refund is paid unconditionally on the trivial "success" [7](#0-6) .

This is precisely the bug class from the external report (Timelock's `executeTransaction` lacking an existence check before treating a call as executed), but reachable by any relayer submitting a proof-backed `GetResponse`/timeout through `HandlerV2` to `EvmHost` — exactly the kind of externally-triggerable delivery path the CallDispatcher (`evm/src/utils/CallDispatcher.sol`) was hardened against with its own `extcodesize` check [8](#0-7) , and that the `PostRequest` variant of `dispatchIncoming` was hardened against, but the `GetResponse`/timeout variants were not.

### Impact Explanation
When the destination module has no code at the moment of delivery (e.g., it self-destructed after dispatching the original GET request/POST request but before the response/timeout returns, or the encoded `from` address is otherwise code-less), the host:
- irreversibly marks the message as handled (deletes replay-protection state / writes a receipt) even though the destination never received or processed anything, permanently losing that message with no retry path, and
- pays the relayer (or refunds the original sender) protocol fees for a delivery that never actually happened.

This is a route that can silently fail to deliver a message while looking successful on-chain, and it misdirects fee accounting — both outcomes the analog validation criteria treat as in-scope (unsound delivery accounting / inability to deliver messages, and unwarranted fee payment).

### Likelihood Explanation
The path is reachable by any relayer who submits a normal `GetResponse` or timeout message through `HandlerV2`/`EvmHost.dispatchIncoming`/`dispatchTimeOut` (both are `restrict(_hostParams.handler)`, i.e., invoked by the permissionless handler on behalf of any relayer with a valid state-machine proof) — no special privilege is required. The triggering condition (destination module code-less at delivery time) is narrower than for an arbitrary user-supplied target, since `from` is fixed to the module that originally dispatched the request rather than attacker-chosen, which lowers likelihood relative to the original Timelock report, but the missing check is a direct, unmitigated code inconsistency versus the already-fixed `PostRequest` sibling.

### Recommendation
Add the same `extcodesize` existence check used in `dispatchIncoming(PostRequest, address)` to `dispatchIncoming(GetResponse, address)` and to both `dispatchTimeOut` overloads before performing the low-level call, and short-circuit (without writing/deleting the receipt or paying any fee) when the destination has no code, mirroring lines 794-803.

### Proof of Concept
1. A module contract `M` on chain A dispatches a `GetRequest` (its address is embedded as `request.from`).
2. Before the corresponding `GetResponse` is relayed back, `M` becomes code-less at that address (self-destruct, or any means by which `extcodesize(M) == 0` at delivery time).
3. A relayer submits the `GetResponse` proof; `HandlerV2` calls `EvmHost.dispatchIncoming(response, relayer)`.
4. `_bytesToAddress(response.request.from).call(...)` at [9](#0-8)  returns `success = true` trivially (EVM low-level call semantics for non-existent code).
5. The host keeps `_responseReceipts[commitment]` (permanently blocking retry), pays the relayer the fee at line 844, and emits `GetRequestHandled` — even though `M.onGetResponse` never ran.

### Citations

**File:** evm/src/core/EvmHost.sol (L794-803)
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

**File:** evm/src/core/EvmHost.sol (L885-900)
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

```

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
```text
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
```
