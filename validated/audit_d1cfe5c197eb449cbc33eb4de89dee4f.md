## Title
Unbounded gas forwarded to `onAccept`/`onGetResponse` callbacks in `EvmHost.dispatchIncoming` lets an attacker-controlled destination app grief relayers and poison batched deliveries - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatchIncoming` invokes the destination application's `onAccept`/`onGetResponse` callback with a bare `.call(...)` that forwards essentially all remaining gas (the standard 63/64 rule, no explicit gas cap). Because the destination `to` address of a cross-chain `PostRequest` is fully attacker-controlled (any contract, on any chain, can dispatch a `DispatchPost` naming an arbitrary destination address), an attacker can deploy a malicious "receiver" contract whose `onAccept` deliberately burns gas. When a relayer submits `HandlerV2.handlePostRequests` (optionally batched with other unrelated messages via `batchCall`), delivering the malicious message costs the relayer far more gas than the fixed relayer fee compensates for, and — because `HandlerV2.batchCall` is documented as atomic ("if any inner call reverts, the whole transaction reverts") — it can also cause co-batched, legitimate messages to fail to deliver in the same transaction.

### Finding Description
`dispatchIncoming(PostRequest, address relayer)` performs: [1](#0-0) 

and `dispatchIncoming(GetResponse, address relayer)` similarly: [2](#0-1) 

Both use a raw `.call(...)` with no `{gas: ...}` qualifier, so Solidity forwards the caller's remaining gas (minus the 1/64 EIP-150 reserve) to the destination contract. The destination address is taken directly from `request.to`/`request.from`, values fully controlled by whoever dispatches the original request on the source chain — there is no allowlist or interface check before the call.

These calls are driven by `HandlerV2.handlePostRequests`, which loops over a relayer-submitted batch of proven requests and calls `host.dispatchIncoming` for each one without any per-call gas limit: [3](#0-2) 

The relayer implementation batches multiple ISMP messages (consensus updates, requests, responses) into a single `HandlerV2.batchCall` transaction for efficiency, and explicitly documents this as all-or-nothing: [4](#0-3) 

An attacker can:
1. Deploy a contract on the destination chain whose `onAccept` (or `onGetResponse`) consumes a very large, attacker-tunable amount of gas (e.g., a bounded busy-loop sized to consume almost all forwarded gas).
2. Dispatch a cheap `DispatchPost`/`Get` from any source chain naming this contract as `to`, paying only the (comparatively small) relayer fee.
3. When any relayer delivers this message — alone or, worse, batched together with other unrelated legitimate messages via `batchCall` — the low-level `.call` in `dispatchIncoming` forwards nearly all remaining gas to the malicious contract, which consumes it. Gas consumed by a sub-call that runs out of gas is not refunded to the caller.

Because `dispatchIncoming` catches the sub-call's failure with `success` and just deletes the pending receipt without reverting, the outer `handlePostRequests`/`batchCall` transaction can still complete "successfully" for that single message — but the gas has already been spent, uncompensated beyond the fixed relayer fee. Worse, if the malicious message is sized to consume gas approaching the full budget allotted to the batch transaction, later iterations in the same `for` loop (processing other, legitimate, batched messages) run out of gas, which (per `batchCall`'s documented atomic semantics) reverts the *entire* transaction — so a single cheap malicious message can prevent delivery of every other message a relayer chose to batch alongside it.

### Impact Explanation
This is directly analogous to the referenced Y2K `Carousel` finding: a `msg.sender`-compensated actor (there, anyone minting queued deposits/rollovers; here, the relayer submitting `handlePostRequests`/`batchCall`) is forced to eat unbounded gas costs dictated by an attacker-controlled callback recipient, for a cost far exceeding what they are paid (`relayerFee`). Concretely:
- Relayers are economically griefed: gas spent delivering a message vastly exceeds the relayer fee collected for it, disincentivizing relaying and potentially making it unprofitable to service the network.
- Batched delivery — the exact mechanism the relayer implementation uses to reduce overhead — can be turned into a denial-of-service primitive: a single cheap malicious message can cause an entire batch transaction (carrying otherwise-valid, unrelated messages) to revert, delaying or blocking delivery of legitimate cross-chain messages ("a route unable to deliver messages", which the validation rules explicitly accept as impact).
- Because it costs only the tiny `DispatchPost` fee to plant a malicious receiver, this is a cheap, repeatable attack an unprivileged message dispatcher can mount against the relayer network at will.

### Likelihood Explanation
Likelihood is high: any address can dispatch a `DispatchPost`/`DispatchGet` naming an arbitrary `to`/`from` contract as destination, no privileged role is required, and `dispatchIncoming`'s unbounded `.call` is unconditional for every incoming message regardless of size or content. The attack requires only deploying a simple gas-burning contract and paying the standard relayer fee for one message.

### Recommendation
- Cap the gas forwarded to application callbacks in `EvmHost.dispatchIncoming` (and the `dispatchTimeOut` variants) to a fixed, documented `maxCallbackGas`, e.g. `destination.call{gas: maxCallbackGas}(...)`, so a misbehaving app can only ever consume a bounded, known amount of gas regardless of how much gas the overall transaction carries.
- Consider exposing this cap as a configurable host parameter (with a sane default) so it can be tuned without a full redeploy, and document it so relayers can safely size batch transactions.
- In `HandlerV2.batchCall`/`handlePostRequests`, consider isolating each message's dispatch (e.g., via a low-level sub-call with its own gas stipend) so a single pathological message cannot exhaust gas for the remainder of a batch, preserving the "cheap batching" optimization without an all-or-nothing DoS surface.

### Proof of Concept
1. Deploy `EvilApp` on the destination EVM chain:
```solidity
contract EvilApp is IApp {
    function onAccept(IncomingPostRequest calldata) external {
        uint256 i;
        // Burn attacker-tunable amount of gas, sized to
        // consume nearly all gas forwarded by EvmHost's .call
        while (gasleft() > 50_000) { i++; }
    }
}
```
2. On the source chain, call `IDispatcher(host).dispatch(DispatchPost({dest: <destChain>, to: abi.encodePacked(evilAppAddr), body: "", timeout: 0, fee: minimalFee, payer: msg.sender}))`.
3. When a relayer processes the proof and calls `HandlerV2.handlePostRequests` (see loop calling `host.dispatchIncoming(leaf.request, _msgSender())` at [3](#0-2) ), the internal `.call` in `EvmHost.dispatchIncoming` ( [5](#0-4) ) forwards nearly all remaining gas to `EvilApp.onAccept`, which is consumed entirely — costing the relayer far more than `minimalFee`.
4. If this message is batched with other legitimate messages via `HandlerV2.batchCall` (as the relayer's `submit_batch_messages` does by default, see [4](#0-3) ), sizing the gas burn appropriately causes the remaining legitimate messages in the loop to run out of gas, reverting the whole batch transaction and preventing delivery of every message in it.

### Citations

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

**File:** tesseract/messaging/evm/src/tx.rs (L441-446)
```rust
/// Submit a full batch of ISMP messages as a single `IHandlerV2.batchCall` transaction.
///
/// One tx replaces what would otherwise be N separate txs (one per message),
/// cutting gas overhead and nonce management complexity. Atomic: if any
/// inner call reverts, the whole transaction reverts.
pub async fn submit_batch_messages(
```
