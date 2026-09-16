Confirmed: the Tron variant of the IntentGateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) has no relayer allowlist mechanism at all (grep for `relayer` matches only the `relayerFee` request parameter and `options.relayerFee` field names, not a `_relayer`/`_checkRelayer` gate), while the canonical EVM contract (`evm/src/apps/intentsv2/ExtrinsicIntents.sol`) enforces `_checkRelayer(incoming.relayer)` as the very first check inside `onAccept` and `onGetResponse` before any request body is decoded.

### Title
Missing relayer authorization gate on Tron's `IntentGatewayV2.onAccept`/`onGetResponse` allows unauthorized delivery of escrow redemption, refund, and governance messages - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The canonical EVM `IntentGatewayV2` (via `ExtrinsicIntents.sol`) fixed a class of forged/unsolicited-delivery risk by requiring that every `onAccept`/`onGetResponse` callback be delivered by a single authorised `_relayer`, checked with `_checkRelayer` before the message body is even decoded [1](#0-0) . The Tron port of the same contract implements the identical `onAccept`/`onGetResponse` logic (RedeemEscrow, RefundEscrow, NewDeployment, UpdateParams, SweepDust) but never calls any relayer check — the gate simply does not exist in that file [2](#0-1) , [3](#0-2) . This mirrors the Obot bug class exactly: a security check exists on one delivery path but was never propagated to a structurally identical parallel path for the same resource, and an unprivileged actor can reach the ungated path directly.

### Finding Description
`onlyHost` still gates the callback to calls coming from the local `EvmHost`/`IHost` contract, so the message must genuinely pass ISMP proof verification through `HandlerV2` before `dispatchIncoming` invokes `onAccept` [4](#0-3) . However, `dispatchIncoming` forwards `relayer = _msgSender()`, i.e., whichever address actually submitted the batch to `HandlerV2.handlePostRequests`/`handleGetResponses` — this is any permissionless relayer, since relaying is intentionally open [5](#0-4) . On the canonical EVM contract, `_checkRelayer` narrows this from "any relayer who can produce a valid proof" down to "only the governance-designated relayer" for the intent gateway's sensitive actions (escrow release/refund and all governance/upgrade paths) [6](#0-5) . That change was deliberately introduced as a security control, as recorded in the project's own changelog for the relayer allowlist on the intent gateway [7](#0-6) . The Tron contract's `onAccept` performs `_authenticate`/source checks against the registered gateway instance for `RedeemEscrow`/`RefundEscrow`, and a Hyperbridge-source check for governance kinds, but has no equivalent of `_checkRelayer` anywhere in the file [2](#0-1) .

### Impact Explanation
Without the relayer gate, on Tron any of Hyperbridge's permissionless relayers (or anyone able to submit a validly-proven ISMP message, which by design is anyone with proofs) can trigger escrow redemption/refund and other `onAccept` logic on this contract as soon as a real cross-chain message exists, without needing to be the address the gateway's operators intended to trust. This is a Medium-to-High severity authorization-model weakening on the Tron deployment: it does not forge messages (ISMP proof verification is still required) but it removes an authorization layer the project explicitly added elsewhere to reduce which relayer can realize escrow payouts, and any unprivileged relayer/token bridger reachable via a single relayed message can act on this parallel gateway deployment where the canonical contract would have reverted with `Unauthorized`.

### Likelihood Explanation
Likelihood is High if the Tron `IntentGatewayV2` is deployed and in active use for cross-chain intents, since exploitation requires nothing more than being one of the permissionless relayers that already deliver ordinary ISMP messages — no special privilege, governance compromise, or malicious node is needed, satisfying the "unprivileged relayer" reachability bar.

### Recommendation
Port the `_relayer` / `_checkRelayer` / `setRelayer` mechanism from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling `_checkRelayer(incoming.relayer)` as the first statement in both `onAccept` and `onGetResponse`, matching the canonical EVM gateway's behavior and test coverage in `evm/tests/foundry/IntentGatewayV2Test.sol`.

### Proof of Concept
1. Deploy/observe the Tron `IntentGatewayV2` and place a cross-chain order whose escrow sits on chain A, destination chain B.
2. Any relayer (not the operator-intended one) fills the order on chain B and relays the resulting `RedeemEscrow` ISMP message to chain A's Tron gateway via `HandlerV2.handlePostRequests`, supplying a valid consensus/state proof (this step requires no special privilege, just normal relaying).
3. `dispatchIncoming` calls `IntentGatewayV2.onAccept` with `incoming.relayer = <arbitrary relayer address>` [5](#0-4) .
4. `onAccept` on Tron proceeds straight to `authenticate(incoming.request)` and `withdraw(...)` with no relayer allowlist check, releasing escrow to the beneficiary encoded in the message body regardless of which relayer submitted it [2](#0-1) , whereas the equivalent call on the canonical EVM `ExtrinsicIntents.onAccept` would revert with `Unauthorized` from `_checkRelayer` for the same non-designated relayer [8](#0-7) .

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L69-78)
```text
    /**
     * @dev Once a relayer is set, rejects deliveries from anyone else before the body is read. The
     * host records the revert as undelivered, so the authorised relayer can resubmit. While unset,
     * every delivery passes: a proxy from before the gate stays open until `migrate` arms it.
     * @param relayer The account that submitted the message to the handler.
     */
    function _checkRelayer(address relayer) internal view {
        address authorised = _relayer;
        if (authorised != address(0) && relayer != authorised) revert Unauthorized();
    }
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-644)
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
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L7-17)
```markdown
1. A relayer calls `HandlerV2.handlePostRequests` (or `handleGetResponses`). After proof
   verification the handler calls `host.dispatchIncoming(request, _msgSender())`. `_msgSender()` is
   plain `msg.sender`; the handler has no trusted forwarder.
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts
   with `Unauthorized` when a relayer is set and the delivery is from anyone else. Only then is the
   first body byte read as a `RequestKind`. `onGetResponse` has the same two steps before touching
   the response.
```

**File:** evm/src/core/EvmHost.sol (L811-818)
```text

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md (L1-10)
```markdown
# 2026-09-03 — Relayer allowlist on the intent gateway

The gateway now accepts `onAccept` and `onGetResponse` deliveries only from a single authorised
relayer stored at `_relayer` (slot 13, packed behind `_paused`). The check runs before the message
body is decoded, so escrow redemptions, refunds and every governance action, upgrades included, are
covered. A refused delivery reverts, which the host records as undelivered, so the authorised
relayer can submit the same message later. `setRelayer(address)` is callable by the immutable
`_owner` and by the host; the host branch exists so a governance `UpgradeContract` can carry the
call as its migration calldata and arm the relayer in the upgrade transaction (`upgradeToAndCall`
delegatecalls that calldata with the host still as `msg.sender`).
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4461-4476)
```text
    function testOnAcceptRejectsUnlistedRelayer() public {
        (PostRequest memory request, bytes32 commitment, uint256 amount) = _escrowedRedeemRequest();

        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: request}));
        assertEq(intentGateway._orders(commitment, address(usdc)), amount, "escrow untouched");
        assertEq(intentGateway._filled(commitment), address(0), "order not finalised");

        // The very same message goes through once the authorised relayer submits it.
        uint256 before = usdc.balanceOf(filler);
        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: request}));
        assertEq(usdc.balanceOf(filler) - before, amount, "authorised relayer releases escrow");
        assertEq(intentGateway._filled(commitment), filler, "order finalised");
    }
```
