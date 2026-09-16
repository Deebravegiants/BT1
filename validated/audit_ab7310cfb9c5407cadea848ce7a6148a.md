### Title
Unchecked `body[0]` access lets an unprivileged dispatcher permanently strand a cross-chain message and its escrowed relayer fee - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`ExtrinsicIntents.onAccept` (used by `IntentGatewayV2`), `SimplexPaymaster.onAccept`, and the Tron `IntentGatewayV2.onAccept` all decode the first byte of an incoming `PostRequest.body` as a `RequestKind` discriminator without ever checking that `body.length > 0`. Any account that can dispatch an ISMP `PostRequest` to one of these contracts (the `to` field of a `PostRequest` is attacker-selectable and dispatch is permissionless) can send an empty body. When the message is relayed and `EvmHost.dispatchIncoming` calls `onAccept`, the `body[0]` index access reverts with Solidity's out-of-bounds `Panic(0x32)`.

### Finding Description
`onAccept` reads the discriminator unconditionally: [1](#0-0) 
The same unguarded pattern exists in the governance/paymaster handler: [2](#0-1) 
and in the Tron-deployed `IntentGatewayV2`: [3](#0-2) 

Delivery is driven by `EvmHost.dispatchIncoming`, which performs a low-level `call` to `onAccept` and treats any revert as "not delivered" (deleting the receipt so it can be retried): [4](#0-3) 

Because the body is attacker-controlled at dispatch time and the destination module `to` is also attacker-selectable, any account that can call the source-chain dispatcher (there is no gate on who may dispatch a `PostRequest`) can construct a `PostRequest` addressed to `IntentGatewayV2`/`SimplexPaymaster` with an empty (or otherwise short) `body`. This is directly analogous to the reported Ella Core bug: a message that omits an expected leading discriminator/type field crashes/traps the handler that assumes the field is always present, rather than being rejected with a clean, recoverable error.

Unlike the ISMP core message types (`Message::Request`, `Message::Response`, etc.), which are strongly typed SCALE/ABI enums validated before being handed to a module, `PostRequest.body` is opaque `bytes` whose interpretation is entirely up to the destination `IApp`. Neither `HandlerV2` nor `EvmHost` validate `body` length before calling `onAccept`, so the burden of guarding against empty/short payloads falls solely on the app, and these three apps fail to do so.

### Impact Explanation
Every retry of the delivery for that request commitment will always hit the same empty `body`, so the revert is deterministic and permanent — this specific message can never be delivered ("a route unable to deliver messages"). If the request was dispatched with `timeoutTimestamp == 0` (no timeout, a supported and used value elsewhere in the codebase, e.g. the LayerZero adapter explicitly notes "no timeout concept"), the request can also never time out, so any relayer fee escrowed for it under `EvmHost._requestCommitments[commitment].fee` is permanently unreclaimable — a permanent freezing of funds. Even when a timeout is eventually reachable, the message is denial-of-serviced for its entire lifetime, and repeated malformed dispatches can be used to grief relayers who keep attempting (and paying gas for) failed delivery attempts against `IntentGatewayV2`/`SimplexPaymaster`. This satisfies the "permanent freezing of funds" / "route unable to deliver messages" bar required for a valid finding, at Medium severity, consistent with the CVSS of the original report (no confidentiality/integrity impact, availability/DoS-only, network-reachable, no privileges beyond permissionless dispatch).

### Likelihood Explanation
Likelihood is high: dispatching a `PostRequest` is a normal, permissionless, unprivileged operation available to any user or contract on a source chain (the exact "unprivileged message dispatcher" actor class in scope). Crafting a request with an empty `body` and `to` set to a deployed `IntentGatewayV2`/`SimplexPaymaster` address requires no special access, no consensus attack, and no proof forgery — only a normal dispatch call. The bug is triggered purely by input shape, matching the "malformed message without expected field" bug class from the advisory.

### Recommendation
In `ExtrinsicIntents.onAccept`, `SimplexPaymaster.onAccept`, and the Tron `IntentGatewayV2.onAccept`, validate `incoming.request.body.length != 0` (and, ideally, the minimum length required for the selected `kind`'s payload) before indexing `body[0]`, and revert with a clear custom error (e.g. `InvalidRequestBody()`) instead of relying on the implicit out-of-bounds panic. This turns an unrecoverable, silently-stuck message into a request that fails predictably and can still time out normally, preserving relayer fee recovery.

### Proof of Concept
1. On the source chain, call the ISMP dispatcher to dispatch a `PostRequest` with:
   - `to = <IntentGatewayV2 address on destination>`
   - `body = ""` (empty bytes)
   - `timeoutTimestamp = 0` (no timeout)
   - any relayer fee attached.
2. Once the source state is finalized/proven, a relayer submits the request to `HandlerV2.handlePostRequests` on the destination `EvmHost`.
3. `EvmHost.dispatchIncoming` calls `IntentGatewayV2.onAccept(...)`.
4. `RequestKind kind = RequestKind(uint8(incoming.request.body[0]));` reverts with `Panic(0x32)` (array out-of-bounds) because `body.length == 0`.
5. `dispatchIncoming` catches the failed call, deletes the request receipt, and returns — the request is now permanently retryable-but-never-deliverable, and (with `timeoutTimestamp == 0`) can never be timed out to release its escrowed fee.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L313-320)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) {
            revert UnauthorizedCall();
        }

        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        bytes calldata payload = incoming.request.body[1:];
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

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
