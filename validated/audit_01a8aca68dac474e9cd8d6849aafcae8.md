Confirmed: all five callback dispatch paths in `EvmHost.sol` (`dispatchIncoming(PostRequest,...)`, `dispatchIncoming(GetResponse,...)`, `dispatchTimeOut(GetRequestTimeout,...)`, `dispatchTimeOut(PostRequestTimeout,...)`) use unbounded `.call()` with return data silently discarded, exactly matching the reported bug class.

### Title
Unbounded return-data copy in EvmHost message delivery calls allows relayer gas-griefing and message delivery denial - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatchIncoming` and `EvmHost.dispatchTimeOut` deliver incoming ISMP messages to destination applications via unbounded low-level `.call()`, discarding the returned bytes with `(bool success,) = ...call(...)`. As documented in the source Spearbit/Fastlane finding, Solidity still copies the entire returned payload into memory before the tuple-assignment discards it, so an attacker-controlled destination contract can force the caller (the relayer's transaction, executing through `HandlerV2`) to pay quadratic memory-expansion costs for an arbitrarily large `RETURNDATACOPY`, exactly the "external calls may use more gas than expected" bug class from the report.

### Finding Description
Every incoming-message delivery path in `EvmHost.sol` forwards the call to an address taken from attacker-influenced request fields and never restricts the callee's returned data size or the gas it may consume relative to what is charged for return-data copying: [1](#0-0) [2](#0-1) [3](#0-2) 

In `dispatchIncoming(PostRequest, address)`, `destination = _bytesToAddress(request.to)` is fully attacker-controlled: any account on any source chain can dispatch a `Post` request whose `to` field addresses a contract they deployed on the destination EVM chain. That contract need not even implement `IApp` — since the call target only needs nonzero `extcodesize`, a bare fallback function that returns a huge payload (e.g. `return(0, 0x100000000)` in assembly) will make `success == true` while still forcing the caller to copy an enormous amount of return data. The same pattern recurs for `onGetResponse` (destination taken from `response.request.from`) and both `onGetTimeout`/`onPostRequestTimeout` timeout callbacks.

None of these four call sites:
- Pass an explicit `gas` stipend to bound the callee's execution,
- Use `ExcessivelySafeCall` or an equivalent return-data-size cap, or
- Skip copying the return data (e.g. via inline assembly `call` + immediate discard without ABI decoding).

This is the precise root cause identified in the external report for `ExecutionEnvironment.sol#L213`: "`.call` copies the entire return data to memory even if it isn't used," which "may use significantly more gas than just the gasLimit value," enabling an adversarial callee to grief the caller.

### Impact Explanation
These calls execute inside `HandlerV2.handlePostRequests` / `handleGetResponses` / timeout-handling entry points, which are the permissionless message-delivery path any relayer uses to deliver proven cross-chain messages, including inside `HandlerV2.batchCall`, which processes multiple messages atomically in one transaction. A malicious application deployed on the destination chain can:
- Force the relayer's transaction to consume drastically more gas than estimated, causing out-of-gas reverts that waste the relayer's gas fee with no compensation, and
- When bundled inside a `batchCall` alongside legitimate messages (as relayers commonly do, per `generate_batched_contract_calls` in `tesseract/messaging/evm/src/tx.rs`), cause the entire batch — including unrelated, legitimate message deliveries — to revert, denying/delaying delivery of those messages ("a route unable to deliver messages").

This directly griefs the relayer network's economics and availability of message delivery, a Medium-risk impact consistent with the original finding's severity rating.

### Likelihood Explanation
Likelihood is high: dispatching a cross-chain `Post`/`Get` request to an attacker-deployed destination contract is a single, unprivileged, permissionless transaction available to any user of the source chain (e.g. via `IDispatcher.dispatch`), and the destination contract requires no special privileges to deploy — only nonzero bytecode. No governance, admin, or relayer collusion is needed to trigger the griefing; it can be repeated cheaply by anyone wanting to disrupt relayer economics or selectively block delivery of a co-batched message.

### Recommendation
Replace the unbounded `.call(...)` pattern in all four `dispatchIncoming`/`dispatchTimeOut` variants with a bounded, return-data-size-capped call — e.g. adopt `ExcessivelySafeCall.excessivelySafeCall(destination, gasLimit, value, maxCopy, data)`, or use raw assembly `call` and skip `RETURNDATACOPY` entirely (matching the `SafeCall.call()` pattern cited by Fastlane's own PR #272 fix for this exact bug class), since the return value from `IApp.onAccept`/`onGetResponse`/`onGetTimeout`/`onPostRequestTimeout` is never consumed. Additionally consider passing an explicit gas stipend to bound callee execution independent of the outer transaction's remaining gas.

### Proof of Concept
1. On the destination EVM chain, deploy `Attacker`:
```solidity
contract Attacker {
    fallback() external payable {
        assembly {
            return(0, 0x100000000) // ~4GB of zeroed return data
        }
    }
}
```
2. From any source chain, dispatch a `PostRequest` whose `to` field encodes `address(Attacker)` (e.g. via any application calling `IDispatcher(host).dispatch(DispatchPost{ to: abi.encode(attacker), ... })`).
3. Once proven, a relayer calls `HandlerV2.handlePostRequests` (optionally batched with other legitimate messages via `batchCall`). `EvmHost.dispatchIncoming` performs `address(destination).call(abi.encodeWithSelector(IApp.onAccept.selector, ...))`; the `Attacker` fallback returns and the EVM begins `RETURNDATACOPY` to build the discarded `bytes memory` value, expanding memory quadratically and consuming gas far beyond what a normal `onAccept` call would require, exhausting the relayer's supplied gas and reverting the whole batch/transaction.

### Citations

**File:** evm/src/core/EvmHost.sol (L794-818)
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
