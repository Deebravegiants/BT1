### Title
Unbounded gas forwarded in `EvmHost.dispatchIncoming` low-level calls enables gas-griefing DoS that can brick message delivery - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming` for both `PostRequest` and `GetResponse` delivery dispatches to attacker-controllable destination modules using a raw `.call(...)` with no explicit gas stipend, forwarding up to 63/64 of all remaining gas (EIP-150) to the destination's `onAccept`/`onGetResponse` callback. A malicious module deployed as the message destination can consume almost all of this forwarded gas, leaving too little gas for the remainder of `dispatchIncoming`'s bookkeeping and for any other unrelated requests batched in the same relayer transaction (via `HandlerV2.handlePostRequests`/`handleGetResponses`), causing the entire outer transaction to revert with an out-of-gas exception instead of failing gracefully per-message.

### Finding Description
`dispatchIncoming(PostRequest ...)` performs: [1](#0-0) 

and `dispatchIncoming(GetResponse ...)`: [2](#0-1) 

Both use a bare `.call(...)` with no `gas:` parameter, meaning nearly all remaining gas in the current call frame is forwarded to the destination module (`request.to` / `response.request.from`), which is an arbitrary address decoded straight from the cross-chain message payload with no whitelist check before the call is attempted.

These calls are reached from `HandlerV2.handlePostRequests` and `HandlerV2.handleGetResponses`, which loop over a batch of requests/responses within a single relayer transaction and call `host.dispatchIncoming` for each one sequentially: [3](#0-2) [4](#0-3) 

Because the module address in a `PostRequest`/`GetResponse` is fully attacker-controlled (any party can dispatch a message from a source chain they control, or in the intents/token-bridge flows, direct calldata to a beneficiary they choose), an attacker can deploy a malicious "destination module" contract whose `onAccept`/`onGetResponse` deliberately consumes gas up to (but just short of) the amount forwarded by the 63/64 rule, engineered so that the *outer* transaction runs out of gas performing subsequent bookkeeping (receipt deletion, event emission, fee transfer) or subsequent loop iterations over other unrelated, legitimate messages batched in the same relayer transaction (e.g. via `HandlerV2.batchCall` or `handlePostRequests`'s per-message loop). Unlike a normal `success == false` failure (which is caught and handled by deleting the receipt so the message can be retried), a mid-batch out-of-gas exception propagates as a revert of the entire enclosing transaction, since Solidity 0.8 EVM OOG failures cannot be caught by the `(bool success,)` pattern once they escape the callee's own gas budget into the caller's remaining execution.

This mirrors the reported analog exactly: an unbounded `.call()` in a dispatch/execute path that lets a malicious counter-party consume all forwarded gas and force an out-of-gas revert, "locking up" the caller's transaction.

### Impact Explanation
A relayer submitting a batch of otherwise-valid, unrelated messages (post requests from many different users/apps) can have the entire batch fail if just one message routes to an attacker-deployed malicious module engineered to grief gas. This degrades to a route that becomes unable to reliably deliver messages: relayers must detect and exclude the malicious message from batches (if even single-message submission is affected, the malicious message itself becomes permanently undeliverable, since `dispatchIncoming`'s early `delete` bookkeeping on failure never executes and the request commitment/receipts are left inconsistent on OOG revert, unlike a clean `success=false` path). This falls under "a route unable to deliver messages" — a High-severity availability/lockup issue for the messaging layer, analogous to the reported BlueBerryBank issue.

### Likelihood Explanation
Likelihood is High: dispatching a `PostRequest` to an arbitrary destination module address is a normal, permissionless operation for any Hyperbridge user/app; deploying a gas-griefing contract as that destination requires no special privilege. Relayers routinely batch multiple unrelated messages together for gas efficiency (`HandlerV2.batchCall`, and the per-message loops in `handlePostRequests`/`handleGetResponses`), which multiplies the blast radius of a single malicious destination.

### Recommendation
Specify an explicit, bounded gas stipend on the low-level calls in `EvmHost.dispatchIncoming` (both overloads), sized to comfortably allow the callback but bounded well below the enclosing transaction's total gas, e.g. `.call{gas: FIXED_CALLBACK_GAS_LIMIT}(...)`. Additionally, ensure enough gas is reserved after the call for the subsequent bookkeeping (`delete`, `emit`, fee transfer) by checking `gasleft()` against a minimum threshold before attempting the call, so a malicious module cannot starve the caller's own state cleanup.

### Proof of Concept
1. Attacker deploys `EvilModule` implementing `IApp.onAccept` that runs a gas-burning loop consuming almost all forwarded gas (e.g. reading many cold storage slots until `gasleft()` is near zero), tuned so ~1/64 of the caller's remaining gas is insufficient for `EvmHost.dispatchIncoming`'s post-call statements.
2. Attacker (or a colluding source-chain module) dispatches a `PostRequest` whose `to` field is `EvilModule`'s address.
3. A relayer includes this request together with N other legitimate `PostRequest`s in one `handlePostRequests` call (or `HandlerV2.batchCall`).
4. When `host.dispatchIncoming` reaches the malicious request, `EvilModule.onAccept` consumes ~63/64 of the remaining gas via the unbounded `.call(...)` at `evm/src/core/EvmHost.sol:809-810`; the leftover 1/64 is insufficient to complete `dispatchIncoming`'s bookkeeping or the remaining loop iterations in `HandlerV2`, causing the entire relayer transaction to revert with out-of-gas.
5. All N legitimate messages batched alongside the malicious one fail to be delivered, and the relayer must identify and exclude the malicious message before resubmitting, effectively letting the attacker unilaterally block delivery of arbitrary co-batched messages at will.

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
