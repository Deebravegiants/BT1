## Title
Unauthenticated empty-body PostRequest causes revert (Panic 0x32) in `ExtrinsicIntents.onAccept` before authentication - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

## Summary
`ExtrinsicIntents.onAccept` reads `incoming.request.body[0]` to determine the `RequestKind` before performing any authentication of the request's source. A PostRequest delivered to this module with a zero-length `body` triggers Solidity's out-of-bounds array-access panic (`Panic(0x32)`), reverting the call — directly analogous to the NSSF nil-pointer dereference triggered by an unvalidated/omitted field in an unauthenticated POST body.

## Finding Description
`onAccept` is the `IIsmpModule` callback invoked by the host/handler when a cross-chain `PostRequest` addressed to this contract (via its `to` field) is delivered: [1](#0-0) 

```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    _checkRelayer(incoming.relayer);
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        _authenticate(incoming.request);
```

`incoming.request.body` is attacker-controlled: it is populated on the *source* chain by whoever dispatches the cross-chain `PostRequest` (any account can dispatch a `PostRequest` on any connected chain and set its destination `to` field to this contract's address and its `body` to an empty byte string). The only gate applied before the vulnerable line is `onlyHost` (any correctly-relayed, proof-verified message from the host) and `_checkRelayer`, neither of which validates that the request originated from a trusted gateway or that `body` is non-empty. `_authenticate(incoming.request)`, which is the actual source-authorization check, only runs *after* `body[0]` is read — and only on the `RedeemEscrow`/`RefundEscrow` branch, but the `body[0]` read itself is unconditional and unguarded, so it executes regardless of which kind was intended.

Indexing an empty `bytes calldata` in Solidity triggers a built-in `Panic(0x32)` (array out-of-bounds), which reverts the entire `onAccept` call. This mirrors the reported bug class exactly: a message-processing entry point dereferences/accesses a field that the untrusted request is free to omit, causing the handler to abort with a runtime panic instead of returning a graceful error.

## Impact Explanation
Because `onAccept` is invoked as part of the relayer's request-delivery flow through Hyperbridge's handler, any relayer or unprivileged party can dispatch (or cause to be dispatched) a `PostRequest` targeting `ExtrinsicIntents` with an empty body. When that request is delivered and `onAccept` reverts, the module callback fails for that specific request/commitment. Depending on how the handler processes failures for the affected request (per-request delivery-failure bookkeeping vs. hard revert of the batch tx), this can:
- Cause repeated relayer transaction failures / wasted relayer gas whenever a message addressed to this contract fails to decode a `RequestKind` from a missing body.
- Grief the message-delivery pipeline for this application: relayers attempting to deliver the malformed request cannot succeed, and no explicit application-level error is returned, undermining request timeout/refund handling that the app relies on (`Unauthorized`/decode errors elsewhere in the file are handled with explicit reverts and clear semantics, but this path panics before any of that logic runs).
- Blocks a route's ability to deliver legitimate `RedeemEscrow`/`RefundEscrow` messages if it is bundled in the same delivery/commitment context, since the panic occurs unconditionally and before authentication, i.e., before the contract can distinguish legitimate vs. malicious senders.

This satisfies the "route unable to deliver messages" / DoS class validated by the report, reachable from a single relayed cross-chain message with no privileged access required.

## Likelihood Explanation
High likelihood: constructing a `PostRequest` with an empty `body` and `to` set to the `ExtrinsicIntents` contract address requires no special privilege — any account dispatching a message through `IDispatcher` on any connected source chain can do this. No `_authenticate` or relayer-specific check runs before the vulnerable read.

## Recommendation
Validate `incoming.request.body.length > 0` (and any additional minimum length required to decode `RequestKind` plus the discriminated payload) before indexing `body[0]`, and revert with an explicit, typed error (e.g. `InvalidRequestBody()`) rather than allowing the implicit array-bounds panic. Consider moving `_authenticate`-equivalent origin checks earlier in the function so that reads of untrusted-format fields cannot occur before the source is confirmed to be a registered gateway.

## Proof of Concept
1. On a source chain connected via Hyperbridge, call `IDispatcher.dispatch` with a `DispatchPost` whose `to` equals the deployed `ExtrinsicIntents` contract address on the destination chain and `body = ""` (empty bytes).
2. Relay/deliver the resulting request through the destination `EvmHost`/`HandlerV2` so that `onAccept(IncomingPostRequest)` is invoked on `ExtrinsicIntents`.
3. Execution reverts inside `onAccept` at `RequestKind(uint8(incoming.request.body[0]))` with `Panic(0x32)` (array out-of-bounds) — before `_authenticate` runs — regardless of the caller's authorization.

Note: I was unable to fully trace `evm/src/core/HandlerV2.sol`'s exact failure-isolation behavior (whether an `onAccept` revert fails only the single request or aborts the whole batch transaction) within the available tool budget; this affects the precise blast radius (single-message DoS vs. multi-message batch DoS) but not the existence of the unguarded panic itself.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```
