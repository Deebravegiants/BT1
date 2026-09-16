### Title
Unvalidated `body[0]` indexing in `IntentGatewayV2.onAccept` allows an unprivileged cross-chain dispatcher to revert message delivery for an entire batch - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.onAccept` reads the request-kind discriminator via `incoming.request.body[0]` without first checking that `body.length > 0` [1](#0-0) . This mirrors the CVE-2024-38562 bug class: consuming an array element (or address-calculated field) before the length that bounds it has been validated. Because `incoming.request` originates from an ISMP `PostRequest` that any source-chain sender can freely construct (destination, body, and length are all attacker-controlled), a zero-length body sent to this module reliably reverts execution inside `onAccept`.

### Finding Description
`HandlerV2.handlePostRequests` verifies the MMR membership proof for a batch of `PostRequestLeaf`s and then calls `host.dispatchIncoming(leaf.request, _msgSender())` for every request in the batch, in a single loop with no per-request try/catch [2](#0-1) . `dispatchIncoming` on the host ultimately invokes the destination module's `onAccept(IncomingPostRequest)` callback.

`IntentGatewayV2.onAccept` immediately dereferences the first byte of the request body to determine `RequestKind`:
```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
``` [1](#0-0) 

There is no guard ensuring `incoming.request.body.length != 0` before this index access. Solidity's calldata-bounds checking will `revert` (rather than corrupt memory as in the C/kernel analog), but the practical effect on message delivery is the same class of defect described in the report: the code performs an access/derivation from an array element whose presence was never validated, based purely on attacker-supplied length.

Since `PostRequest.body` and `PostRequest.dest` are both fully attacker-controlled by whoever dispatches on the source chain (via `EvmHost.dispatch`/`IDispatcher.dispatch`), any account can craft a `PostRequest` with `dest = IntentGatewayV2` and `body = ""` (zero-length). Once relayed and included in `handlePostRequests`, this reverts inside `onAccept`, and since the outer loop has no isolation, the entire batch transaction reverts — including all other legitimate requests bundled in the same MMR-proof batch by the relayer.

### Impact Explanation
This directly maps to the "route unable to deliver messages" acceptance criterion: a single unprivileged, cheaply-crafted cross-chain request can force reversion of `HandlerV2.handlePostRequests` for the whole batch it is included in, denying delivery of unrelated legitimate requests processed in the same relayer transaction. Relayers must special-case or exclude any request destined for `IntentGatewayV2`, and until they do, message delivery to/through this route can be repeatedly griefed by any actor able to dispatch a request from a source chain (a normal, permissionless operation).

### Likelihood Explanation
High feasibility: dispatching an ISMP `PostRequest` with an arbitrary destination and an empty body is a standard, permissionless operation available to any address on any connected chain — no privileged role, governance, or admin access is required. The only requirement is paying the request's dispatch fee.

### Recommendation
Add an explicit length check at the top of `onAccept` before indexing, e.g.:
```solidity
if (incoming.request.body.length == 0) revert InvalidRequestBody();
RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
```
Additionally, consider making `HandlerV2.handlePostRequests`/`handleGetResponses` resilient to a single destination module reverting (e.g., wrap `dispatchIncoming` per-request in a try/catch and emit a delivery-failure event) so a single malformed or malicious request cannot take down delivery of an entire batch.

### Proof of Concept
1. On any source chain, call the ISMP host's dispatch function with a `PostRequest` where `dest` = the target chain's `IntentGatewayV2` address and `body = 0x` (empty), paying the applicable relayer fee.
2. A relayer collects this request together with other unrelated legitimate requests into one MMR-proof batch and calls `HandlerV2.handlePostRequests`.
3. Proof verification succeeds (crafting the request costs nothing to be valid), and the loop reaches `host.dispatchIncoming(leaf.request, _msgSender())` for the malicious leaf, which calls `IntentGatewayV2.onAccept`.
4. `RequestKind(uint8(incoming.request.body[0]))` reverts due to out-of-bounds access on the empty `body`, unwinding the entire `handlePostRequests` transaction and denying delivery of every other request batched alongside it. [1](#0-0) [2](#0-1)

### Citations

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
