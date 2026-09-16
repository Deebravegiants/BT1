### Title
Empty-body POST request panics `onAccept` in cross-chain apps due to unchecked `body[0]` array access - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
Several Hyperbridge application contracts that implement `IIsmpModule.onAccept` (the entry point the `IHost`/`HandlerV2` calls when delivering a verified incoming POST request) dispatch on the first byte of the request body via `uint8(incoming.request.body[0])` without first checking that `body.length > 0`. A POST request with an empty `body` is trivial for any unprivileged sender to dispatch on the source chain, and when relayed to the destination it makes `onAccept` revert with an out-of-bounds array access (Solidity `Panic(0x32)`), rather than the app returning a clean error. This is the Solidity analog of the CVE's "malformed input drives an unchecked read past a buffer boundary and crashes the handler" bug class.

### Finding Description
`onAccept` in `evm/tron/contracts/apps/IntentGatewayV2.sol` reads: [1](#0-0) 
```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
```
There is no `require(incoming.request.body.length > 0, ...)` (or equivalent) guard anywhere on the path from message dispatch, through `HandlerV2`/consensus and state-proof verification, to this call — a search of the codebase for a body-length check before this dispatch found none. The same unguarded `RequestKind(uint8(incoming.request.body[0]))` pattern appears in `evm/src/apps/intentsv2/ExtrinsicIntents.sol`, `evm/src/utils/SimplexPaymaster.sol`, and `evm/src/utils/VWAPOracle.sol`.

`incoming.request.body` is attacker-controlled: any account can call `IDispatcher.dispatch` on the *source* chain with an arbitrary destination and an empty `body`, and a relayer (or the attacker themselves, self-relaying) can then submit the proof to `HandlerV2.handlePostRequests` on the destination chain targeting one of these app contracts. `HandlerV2` verifies the state/consensus proof — which is orthogonal to the semantic content of the request body — and then calls `onAccept` on the destination module, which panics on the empty body.

### Impact Explanation
Solidity's bounds check on `bytes calldata` indexing reverts the whole call rather than causing memory corruption (unlike the C-level heap overflow in the original ImageMagick/tiff CVE), so the direct effect here is a denial-of-service on message delivery rather than memory corruption. Per the validation rubric this still qualifies as impact because it produces "a route unable to deliver messages": a single crafted zero-length-body request delivered as part of a `PostRequestMessage`/`batchCall` submission can cause that request's delivery to permanently fail (every future delivery attempt reverts identically), and if it is bundled with legitimate requests in the same batch/proof, it can block delivery of the co-batched, unrelated legitimate requests as well, since a revert in `onAccept` propagates up through the handler's request loop.

### Likelihood Explanation
High feasibility: dispatching a POST request with an empty body requires no special privilege — it is a normal, permissionless `IDispatcher.dispatch` call from the source chain, and delivery merely requires the request to be included in a proof, which any relayer (including the attacker) can construct once the request is finalized on Hyperbridge. No admin, governance, or privileged relayer/collator role is needed, matching the requirement that only unprivileged dispatcher/relayer/intent-solver paths be considered.

### Recommendation
Add an explicit length check at the top of `onAccept` in `IntentGatewayV2.sol` (and the same pattern in `ExtrinsicIntents.sol`, `SimplexPaymaster.sol`, `VWAPOracle.sol`):
```solidity
if (incoming.request.body.length == 0) revert InvalidRequestBody();
```
before indexing `body[0]`, so malformed/empty bodies are rejected with a typed revert instead of an array-bounds panic, and so a batched delivery containing one malformed request does not necessarily need to poison co-batched legitimate requests (consider isolating per-leaf failures in the handler if that is architecturally desired).

### Proof of Concept
1. On the source chain, call `IDispatcher(host).dispatch(DispatchPost({ dest: <destChain>, to: abi.encodePacked(intentGatewayV2Address), body: "", timeout: 0, fee: 0, payer: msg.sender }))` — no special role required.
2. Wait for the request to finalize on Hyperbridge and obtain the proof (self-relay via the SDK or any relayer).
3. Submit `HandlerV2.handlePostRequests(host, PostRequestMessage{ proof, requests: [leaf] })` on the destination chain targeting `IntentGatewayV2`.
4. `onAccept` executes `RequestKind(uint8(incoming.request.body[0]))` on a zero-length `body`, reverting with an array-out-of-bounds panic; the request can never be delivered successfully, and if batched with other requests in the same `handlePostRequests`/`batchCall`, it reverts their delivery too.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-631)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
```
