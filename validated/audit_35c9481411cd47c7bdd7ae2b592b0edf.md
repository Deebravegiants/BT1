Found this in `evm/tron/contracts/apps/IntentGatewayV2.sol:630` — `onAccept` reads `incoming.request.body[0]` and `incoming.request.body[1:]` without checking that `body.length` is non-zero, an unguarded array-index read directly analogous to the CVE's out-of-array read in a decoder, reachable from any relayer delivering a forged/empty-bodied cross-chain message.### Title
Unchecked `body[0]` index read in `IntentGatewayV2.onAccept` allows an empty-bodied POST request to panic/revert the intent settlement path - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.onAccept()` dereferences `incoming.request.body[0]` before validating that `body` is non-empty, mirroring the out-of-array-read bug class in CVE-2018-6912 (`decode_plane` reading past the end of an attacker-supplied buffer without a length check).

### Finding Description
`onAccept` is the ISMP delivery entrypoint the `EvmHost`/`HandlerV2` calls when a relayer delivers a cross-chain POST request destined for the intent gateway: [1](#0-0) 

```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        authenticate(incoming.request);
        WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
        return withdraw(body, kind == RequestKind.RefundEscrow);
    }
```

`incoming.request.body` comes straight from a relayer-supplied, MMR/state-proof-verified `PostRequest` and is only bounds-checked by whatever the *source* chain happened to encode — nothing on this (destination) chain guarantees `body.length >= 1` before `onAccept` indexes `body[0]`. Solidity's `calldata bytes` indexing (`body[0]`) reverts with a low-level index-out-of-bounds panic rather than a clean, typed error when `body.length == 0`. This is architecturally the same root cause as the FFmpeg CVE: a decoder consumes a fixed offset from attacker-controlled data without first checking the buffer is long enough.

The reachability differs from the earlier "already patched" instances found elsewhere in this codebase (e.g. `modules/trees/ethereum/src/node_codec.rs` empty-HP-prefix guard, `pharos` `nibble_at_depth` depth guard, BEEFY `mmr.leaf_indices` guard, sync-committee `multi_proof` length guard) — all of which had been hardened with explicit length checks and regression tests. `IntentGatewayV2.onAccept` has no equivalent guard.

### Impact Explanation
Any state machine capable of dispatching an ISMP POST request to the `IntentGatewayV2` address (a compromised/forged/legacy peer instance, or a message the destination's `EvmHost` accepts as coming from an unregistered/attacker-influenced `instance()`), or any relayer relaying a message whose `body` field was legitimately empty (e.g. a malformed/degenerate request that still passes membership/consensus verification because verification only covers commitment integrity, not application-level body shape), will cause `onAccept` to revert with an out-of-bounds panic instead of a handled error. Because `onAccept` is invoked by `HandlerV2`/`EvmHost` as part of the generic message-delivery batch call, a single malformed request can:
- Revert the whole delivery transaction (denial of service for that batch of requests/timeouts being processed together), and
- More importantly, since there is no upfront length validation, any code path that assumes `kind` was decoded from a validated buffer (e.g. the fallthrough after the `if` for `NewDeployment`/`UpdateParams`/`SweepDust`) is reached only after this unguarded read, so a hostile "empty body" cannot even be distinguished/rejected with a typed revert — it always panics.

This qualifies as "a route unable to deliver messages": it lets an attacker DoS the intent-gateway's inbound message path by causing reverts on the shared `onAccept` handler rather than a documented `revert` such as `Unauthorized()`/`WrongChain()`.

### Likelihood Explanation
Likelihood is **Medium**: `onAccept` is `onlyHost`-gated, so triggering it directly requires convincing the local `EvmHost` to deliver a POST request with an empty body and `request.from == instance(request.source)` (registered peer) — or exploiting any state machine (chain) whose registered `instance()` is compromised or misconfigured. It does not require a malicious admin/governance action; it only requires a relayer to successfully deliver a proof-verified message whose `body` field is empty, which the base ISMP delivery/proof-verification layer never rejects (body shape is application-defined, not protocol-defined).

### Recommendation
Validate `incoming.request.body.length > 0` (and, ideally, the minimum length expected for each `RequestKind`, e.g. `>= 1 + abi_encoded_length`) at the top of `onAccept` before indexing or slicing, returning a typed revert (e.g. `InvalidRequestBody()`) instead of relying on Solidity's implicit array-bounds panic. Apply the same explicit length check to any other `onAccept`/`onPostRequestTimeout` implementations in the codebase that index `body[0]`/`body[1:]` without a prior length check (the same `RequestKind(uint8(incoming.request.body[0]))` pattern also appears in `evm/src/apps/intentsv2/ExtrinsicIntents.sol`, `evm/src/utils/SimplexPaymaster.sol`, and `evm/src/utils/VWAPOracle.sol`, which should be audited/patched identically).

### Proof of Concept
1. Register (or compromise) a source `StateMachine` entry via `_instances[keccak256(stateMachineId)]` so that `IntentGatewayV2.onAccept`'s `authenticate`/source checks for `NewDeployment`-style requests can be satisfied, or find any path where the host delivers a POST request from `hyperbridge()` or a registered peer.
2. Craft a `PostRequest` whose `body` field is the empty byte string (`""`) and get it through consensus/state-proof verification (verification only checks the request commitment/membership, not that `body.length > 0`).
3. Relay this request through `HandlerV2.handlePostRequests`, which calls `EvmHost` → `IntentGatewayV2.onAccept(incoming)`.
4. `uint8(incoming.request.body[0])` on a zero-length `calldata bytes` triggers an EVM panic (`Panic(0x32)` – array out-of-bounds access), reverting the entire batch delivery transaction instead of returning a clean, typed error.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```
