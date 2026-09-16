## Title
Unhandled out-of-bounds revert on empty POST-request body in Intent Gateway `onAccept` can DoS an entire batch delivery - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol` / `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`ExtrinsicIntents.onAccept` and `IntentGatewayV2.onAccept` both begin by reading the first byte of the incoming request body without checking its length:

```solidity
RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
``` [1](#0-0) [2](#0-1) 

If `incoming.request.body` is empty (a source-chain sender can dispatch an ISMP POST request with a zero-length body targeting the Intent Gateway module), `body[0]` reverts.

### Finding Description
`onAccept` is invoked by `EvmHost.dispatchIncoming`, which is called in a loop from `HandlerV2.handlePostRequests` for every leaf in a relayed batch:
```solidity
for (uint256 i = 0; i < requestsLen; ++i) {
    ...
    host.dispatchIncoming(leaf.request, _msgSender());
}
``` [3](#0-2) 

There is no `try/catch` around this dispatch — a revert inside `onAccept` propagates and reverts the whole `handlePostRequests` transaction, including all other (unrelated, legitimate) requests batched alongside it.

Any unprivileged actor that can dispatch an ISMP POST request from a source chain (e.g. via the source chain's `IDispatcher`) can target the Intent Gateway address as destination with a zero-length body. Once relayed and included in a `handlePostRequests` batch together with legitimate requests, delivery of the entire batch reverts.

### Impact Explanation
This is analogous in bug-class to CVE-2021-40516 (an attacker-controlled message triggering an out-of-bounds/unchecked read that a remote message dispatcher can reach), but the concrete effect here is a "route unable to deliver messages" condition: a single crafted zero-byte-body message can grief a relayer's batch and delay/deny delivery of otherwise-valid POST requests batched together, which is a Medium-severity denial-of-service on message delivery rather than fund loss.

### Likelihood Explanation
Likelihood is Medium: dispatching an ISMP POST request with an empty body toward an arbitrary destination address is a normal, permissionless action available to any user of `IDispatcher.dispatch` on a source chain that has this app deployed; no special permission or specific proof state is required, though it depends on the relayer's batching strategy for it to actually affect other requests.

### Recommendation
Validate `incoming.request.body.length > 0` at the top of `onAccept` and revert with a clear, low-gas error (e.g. `InvalidRequestBody()`), or have `HandlerV2.handlePostRequests` execute each `dispatchIncoming` call in an isolated try/catch analogous to the pattern already used in `HyperbridgeLzEndpoint.onAccept`'s `try/catch` around `lzReceive`, so a single malformed message cannot revert delivery of an entire batch.

### Proof of Concept
1. On the source chain, call `IDispatcher(host).dispatch(DispatchPost({dest: <destChain>, to: abi.encodePacked(intentGatewayAddress), body: "", timeout: 0, fee: 0, payer: attacker}))` with an empty `body`.
2. Wait for/force a relayer to include this request's leaf alongside other legitimate leaves in a single `handlePostRequests` call on the destination `HandlerV2`.
3. `EvmHost.dispatchIncoming` calls `IntentGatewayV2/ExtrinsicIntents.onAccept`, which executes `RequestKind(uint8(incoming.request.body[0]))` on an empty `bytes calldata`, causing a revert.
4. The revert propagates up through `dispatchIncoming` and `handlePostRequests`, reverting the whole batch and denying delivery to all co-batched requests.

Note: because this analysis is based on static code review of the indexed snippets, I was not able to execute a live Foundry test to confirm the exact revert propagation path through `EvmHost.dispatchIncoming` (that file's `dispatchIncoming` body was not returned in my searches); a Devin session with full repo access would be needed to confirm there is no existing try/catch wrapper inside `dispatchIncoming` itself before treating this as fully validated.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-332)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-630)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
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
