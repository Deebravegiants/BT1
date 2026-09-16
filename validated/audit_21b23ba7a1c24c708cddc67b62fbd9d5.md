### Title
`EvmHost` dispatches incoming messages to attacker-controlled destinations via unguarded low-level `.call()`, exposing relayers to a return-bomb gas-griefing DoS - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatchIncoming` and `EvmHost.dispatchTimeOut` deliver incoming POST requests, GET responses, and timeouts to destination application contracts using a bare `address.call(...)` with no gas cap and no bound on the copied return data, mirroring the GMX `CallbackUtils` return-bomb pattern. Because the destination (`request.to`/`request.from`) is attacker-controllable (any account can dispatch a POST request to an arbitrary contract address), an attacker can deploy a malicious `IApp` that returns/reverts with an enormous payload, forcing the relayer's transaction to pay a large, unbounded memory-expansion cost when Solidity copies the returndata back into the caller's frame — burning the relayer's gas and potentially aborting the entire batched delivery.

### Finding Description
`dispatchIncoming(PostRequest, address)` performs:
```solidity
(bool success,) = address(destination)
    .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));
``` [1](#0-0) 

The same unguarded pattern is repeated for GET responses and both timeout paths: [2](#0-1) [3](#0-2) [4](#0-3) 

None of these calls set an explicit `{gas: ...}` stipend nor use a returndata-size-limited call helper (e.g. `excessivelySafeCall`). In Solidity, a low-level `call` unconditionally uses `RETURNDATACOPY` to materialize the callee's return/revert data into memory in the *caller's* execution context — regardless of whether the second tuple element is bound to a variable. The cost of this copy is dominated by quadratic memory-expansion gas, paid by the caller (i.e. the relayer submitting the batch), not the callee.

These entry points are reached from `HandlerV2`, which iterates over an entire batch of proof-verified messages in a single transaction and calls `host.dispatchIncoming`/`host.dispatchTimeOut` for each item in a loop, e.g.: [5](#0-4) [6](#0-5) 

Because `to`/`from` in a `PostRequest` is a raw address chosen by the original dispatcher (any unprivileged account can dispatch a POST request targeting an arbitrary contract on the destination chain), an attacker can deploy a contract at that destination whose `onAccept` (or `onGetResponse`/`onPostRequestTimeout`/`onGetTimeout`) reverts with a multi-hundred-KB `reasonBytes` (or simply returns such a payload on success). When the relayer's batch transaction reaches this malicious entry in the loop, the implicit returndata copy in `EvmHost` consumes gas proportional to the (attacker-chosen) size of the returned bytes, which can be made large enough to exhaust the remaining gas of the whole batched transaction.

### Impact Explanation
This gives an unprivileged attacker a griefing/denial-of-service primitive against message delivery:
- A single malicious message can be embedded in (or targeted alongside) a batch of otherwise legitimate `handlePostRequests`/`handleGetResponses`/`handlePostRequestTimeouts`/`handleGetRequestTimeouts` calls, causing the whole batch transaction to run out of gas and revert, so legitimate cross-chain messages sharing the batch fail to be delivered ("a route unable to deliver messages").
- Relayers pay gas for the entire transaction up to failure, so this can be used to repeatedly burn relayer gas, discouraging relayers from delivering messages to or interacting with the batch, and can be weaponized to selectively stall delivery/timeout processing (e.g., to protect an out-of-the-money position from `onPostRequestTimeout`/timeout-driven refunds, analogous to the original GMX report's "risk free trade" scenario), since a failed timeout dispatch reverts state changes for the fee refund path as well.

### Likelihood Explanation
Likelihood is high: any account can dispatch a POST request (or become the source of a GET request) whose `to`/`from` field points to an attacker-deployed contract; no special privilege or governance action is required, and the destination contract's existence check only verifies non-zero code size, not that it behaves honestly. Relayers process batches permissionlessly, so an attacker only needs to get one malicious request into (or share a batch window with) a target batch.

### Recommendation
Bound both the gas and the copied return-data size for all destination calls in `EvmHost`:
- Explicitly cap forwarded gas with `{gas: request.gasLimit}`-style parameters bounded by a sane maximum.
- Use a returndata-size-limited call helper (e.g., `ExcessivelySafeCall.excessivelySafeCall`) instead of a raw `.call(...)`, so the callee cannot force the caller to copy an attacker-chosen amount of return data. Apply this to `dispatchIncoming(PostRequest, address)`, `dispatchIncoming(GetResponse, address)`, `dispatchTimeOut(GetRequestTimeout, ...)`, and `dispatchTimeOut(PostRequestTimeout, ...)` in `evm/src/core/EvmHost.sol`.

### Proof of Concept
1. Attacker deploys `MaliciousApp` implementing `IApp.onAccept` that, on invocation, either reverts with `revert(largeBytes)` where `largeBytes` is hundreds of KB, or simply returns such data before reverting/succeeding.
2. Attacker (any unprivileged account) dispatches a `DispatchPost` request via a source-chain application whose `to` field is `MaliciousApp`'s address.
3. A relayer submits a `handlePostRequests` batch that includes this request together with other legitimate requests, verified by a valid membership proof.
4. When `HandlerV2.handlePostRequests` reaches the malicious leaf and calls `host.dispatchIncoming(leaf.request, relayer)` [5](#0-4) , `EvmHost.dispatchIncoming`'s low-level call to `MaliciousApp.onAccept` [1](#0-0)  forces the parent frame to copy the huge returndata into memory, consuming gas quadratically.
5. With a sufficiently large `reasonBytes`/return payload, the batch transaction runs out of gas before finishing processing of the remaining (legitimate) leaves, causing the entire batch — and any legitimate messages bundled with it — to fail delivery, while the relayer's gas is consumed.

### Citations

**File:** evm/src/core/EvmHost.sol (L809-810)
```text
        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));
```

**File:** evm/src/core/EvmHost.sol (L832-833)
```text
        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));
```

**File:** evm/src/core/EvmHost.sol (L863-864)
```text
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));
```

**File:** evm/src/core/EvmHost.sol (L892-893)
```text
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onPostRequestTimeout.selector, timeout));
```

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

**File:** evm/src/core/HandlerV2.sol (L241-246)
```text
        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
```
