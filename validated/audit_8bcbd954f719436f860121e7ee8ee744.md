## Analog Found

### Title
Missing length check before indexing `request.body[0]` allows a zero-length POST body to revert an entire batched message delivery - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
The Linux HIDP bug is a missing length/discriminant validation: the code compares an expected report number against a payload byte without first confirming the payload contains that byte, so a crafted peer response with an empty payload triggers undefined/unsafe behavior. The same bug class — reading a "kind"/discriminant byte from a message body without checking the body is non-empty — appears in Hyperbridge's `onAccept` handlers, which decode `RequestKind` straight from `body[0]` of an untrusted, relayer-delivered `PostRequest`.

### Finding Description
`ExtrinsicIntents.onAccept` and `SimplexPaymaster.onAccept` both do: [1](#0-0) [2](#0-1) 

`RequestKind kind = RequestKind(uint8(incoming.request.body[0]));` reads the first byte of `body` with no `body.length > 0` guard. `body` originates from a `PostRequest` that is fully attacker/relayer controlled content (only the ISMP membership proof and `from`/`source` fields are cryptographically checked; the byte content of `body` is not constrained to be non-empty). A `PostRequest` with `body.length == 0` targeting either app causes `body[0]` to revert with a Solidity out-of-bounds panic.

Crucially, `HandlerV2.handlePostRequests` dispatches every request in a proven batch in a plain loop with no per-request isolation (no `try/catch`): [3](#0-2) 

Because `dispatchIncoming` is called directly rather than isolated, a single malformed (empty-body) request embedded in a relayer's batch reverts the *entire* `handlePostRequests` transaction — including all unrelated, legitimate requests bundled in the same MMR-proof batch. This mirrors the HIDP flaw's root cause: a numbered/kind-tagged payload is dereferenced before its length is validated, and an unprivileged party (any relayer or, indirectly, any user who can get a message routed to these apps' `to` address) can supply the malformed shape.

### Impact Explanation
Unlike the kernel bug (which risks uninitialized-memory disclosure), this is not a memory-safety issue in Solidity — `body[0]` on an empty `bytes` reverts rather than reading garbage. However, the consequence is a denial of message delivery: any relayer batch containing one crafted empty-body request destined for `ExtrinsicIntents` or `SimplexPaymaster` fails entirely, so legitimate requests bundled with it cannot be delivered in that submission. Since Hyperbridge batches many requests per MMR multiproof to amortize proof-verification gas, this allows a single adversarial request (dispatched from any source chain to the victim app's address) to repeatedly block delivery of a shared batch, i.e., "a route unable to deliver messages" for co-batched requests, until relayers learn to exclude/reorder around the poison message.

### Likelihood Explanation
Reachable by anyone who can get a `PostRequest` with `to == ExtrinsicIntents` or `to == SimplexPaymaster` and an empty `body` included into a relayed batch — this requires no privileged role, only a source-chain dispatch (or a malicious/careless relayer aggregating requests), matching the "unprivileged message dispatcher/relayer" reachability the analog scope requires.

### Recommendation
Add an explicit `require(incoming.request.body.length > 0)` (or equivalent revert) at the top of `onAccept` in both `ExtrinsicIntents.sol` and `SimplexPaymaster.sol` before indexing `body[0]`, and consider isolating per-request dispatch failures in `HandlerV2.handlePostRequests`/`handleGetResponses` (e.g., `try/catch` around `dispatchIncoming`, marking the request receipt regardless of app-level failure) so one malformed or reverting request cannot block delivery of the rest of a proven batch.

### Proof of Concept
1. Relayer/attacker constructs (or gets included in a batch) a `PostRequest` with `dest` = the chain hosting `ExtrinsicIntents`, `to` = the `ExtrinsicIntents` contract address, and `body = ""` (zero bytes).
2. This request, along with N legitimate requests, is proven via a valid MMR multiproof and submitted to `HandlerV2.handlePostRequests`.
3. During the dispatch loop, `host.dispatchIncoming` invokes `ExtrinsicIntents.onAccept`, which executes `RequestKind(uint8(incoming.request.body[0]))` on an empty `body`, causing an out-of-bounds panic.
4. The panic propagates up through the un-isolated loop in `HandlerV2.handlePostRequests`, reverting the whole transaction and failing to deliver all N legitimate co-batched requests.

**Note on confidence:** I was not able to fully trace `EvmHost.dispatchIncoming`'s exact internal call path (whether it adds any panic isolation before calling `IApp.onAccept`) within the available search results — the snippet I found in `HandlerV2.sol` shows the outer loop calling `dispatchIncoming` with no `try/catch`, but I could not locate and read the full body of `dispatchIncoming` in `EvmHost.sol` to confirm there is no internal try/catch there. If `dispatchIncoming` internally wraps the `onAccept` call in `try/catch`, the batch-wide DoS impact described above would not hold, and the bug would degrade to a single-message revert (self-contained, lower severity, and likely out of scope per the analog rules).

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L313-321)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) {
            revert UnauthorizedCall();
        }

        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        bytes calldata payload = incoming.request.body[1:];

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
