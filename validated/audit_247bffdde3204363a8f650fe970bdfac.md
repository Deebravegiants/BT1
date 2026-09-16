### Title
Empty POST-request body reaching `IntentGatewayV2.onAccept` reverts on `body[0]` index access, permanently bricking that message and any batch it is delivered in - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.onAccept` reads `incoming.request.body[0]` to select the `RequestKind` *before* checking that `request.source` matches an authorized sender, mirroring the CVE-2024-50608 bug class: a zero-length payload dereferenced/indexed without a length check crashes the handling path. Because a POST request's `body` is fully attacker-controlled by whoever dispatches the message on the source chain, and `to` (the destination module) is likewise attacker-chosen, any unprivileged sender on any connected chain can dispatch a request with an empty `body` targeting this contract's address, which a relayer will eventually attempt to deliver.

### Finding Description
`onAccept` does:
```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    ...
``` [1](#0-0) 

There is no `require(request.body.length > 0)` guard, and — critically — the `source == hyperbridge` authorization check happens *after* this line:
```solidity
RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
    authenticate(incoming.request);
    ...
}
if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
``` [1](#0-0) 

Since `incoming.request.body[0]` on an empty `bytes calldata` array triggers Solidity's out-of-bounds panic (revert), any account able to dispatch an ISMP POST request whose `to` targets this contract with `body = ""` can force `onAccept` to always revert for that specific message — regardless of source. Delivery of a POST request on the destination chain happens via `HandlerV2.handlePostRequests`, which loops over all batched requests and calls `host.dispatchIncoming(leaf.request, _msgSender())` with no `try/catch`:
```solidity
for (uint256 i = 0; i < requestsLen; ++i) {
    PostRequestLeaf memory leaf = request.requests[i];
    if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
    host.dispatchIncoming(leaf.request, _msgSender());
}
``` [2](#0-1) 

`dispatchIncoming` ultimately calls the destination module's `onAccept`. If `onAccept` reverts, the entire batched `handlePostRequests` transaction reverts — including delivery of any legitimate, unrelated requests bundled in the same relayer submission. Because the request's contents (including the empty body) are committed into the MMR at dispatch time on the source chain, the malformed request can never successfully be delivered: every relayer attempt to include it in a batch will always revert at the same `body[0]` access, permanently freezing that request (and threatening co-batched requests) — the destination route for that message becomes permanently undeliverable.

### Impact Explanation
This is a Denial-of-Service against a specific message path rather than fund theft: a request dispatched to `IntentGatewayV2` with an empty body can never be executed, and if a relayer naively batches it with other pending requests, the whole batch's other (legitimate) requests also fail to be delivered in that transaction, wasting relayer gas and delaying delivery of unrelated messages until the relayer identifies and isolates the poisoned commitment. This matches the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
High likelihood of triggerability: dispatching a POST request with `to = <IntentGatewayV2 address>` and `body = ""` from any source chain requires no special privilege — it is a normal, permissionless `IDispatcher.dispatch` call available to any account. The relayer network processes all pending requests, so eventually a relayer will attempt (and permanently fail) to deliver it.

### Recommendation
1. In `IntentGatewayV2.onAccept`, add `if (incoming.request.body.length == 0) revert InvalidRequestBody();` before reading `body[0]`.
2. Move the `source`/authorization check ahead of the `RequestKind` decode where possible, so unauthorized/malformed requests from arbitrary sources fail fast without touching potentially malformed body data.
3. Consider having `HandlerV2.dispatchIncoming` (or the loop in `handlePostRequests`/`handleGetResponses`) wrap the module call in a try/catch so that one malformed/reverting request cannot block delivery of the rest of a batch, converting an unrecoverable revert into a per-message failure receipt instead.

### Proof of Concept
1. On any source chain, an unprivileged account calls the local ISMP dispatcher with:
   - `dest` = the chain hosting `IntentGatewayV2`
   - `to` = `IntentGatewayV2`'s address (ABI-encoded)
   - `body` = `""` (empty bytes)
2. The request is committed to the source chain's outgoing MMR and eventually picked up by relayers.
3. A relayer submits `HandlerV2.handlePostRequests` with this request (possibly batched with others).
4. `host.dispatchIncoming` invokes `IntentGatewayV2.onAccept`, which executes `uint8(incoming.request.body[0])` on a zero-length `body`, reverting.
5. Because there's no try/catch, `handlePostRequests` reverts entirely; any other requests batched with it fail to be delivered in that transaction. The malformed request's content is fixed by the MMR commitment, so every future delivery attempt for it fails identically — it can never be delivered.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-638)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
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
