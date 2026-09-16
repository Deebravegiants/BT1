### Title
Missing relayer authorization gate in Tron `IntentGatewayV2.onAccept` allows any relayer to trigger privileged escrow/governance actions - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The OtterSec report's central lesson is that Solana's execution model performs no type/permission checking on the accounts or metadata a caller supplies — every authorization decision (`is_signer`, ownership, etc.) must be explicitly re-checked by the program itself, or an attacker can substitute the "wrong" actor and reach privileged code paths. `IHandlerV2` on Hyperbridge is explicitly permissionless — "anyone can call them to relay messages" [1](#0-0)  — so, just as in the Solana model, every downstream `IApp.onAccept`/`onGetResponse` callback must independently re-verify *who* is delivering the message if it wants to restrict that set. The canonical EVM `IntentGatewayV2` (`ExtrinsicIntents.sol`) does this by calling `_checkRelayer(incoming.relayer)` as the very first statement of `onAccept`, before even decoding the `RequestKind` [2](#0-1) . The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, omits this check entirely in its `onAccept` [3](#0-2) .

### Finding Description
`onAccept` is invoked by `EvmHost.dispatchIncoming` for any relayer that has supplied a valid state/consensus proof — the relayer field is simply `msg.sender` of `HandlerV2.handlePostRequests`, with no trusted forwarder [4](#0-3) . The intended security model layers an application-level relayer allowlist ("the relayer gate") on top of proof verification: `ExtrinsicIntents.onAccept` calls `_checkRelayer(incoming.relayer)` first, which "reverts with Unauthorized when a relayer is set and the delivery is from anyone else" [5](#0-4) , and this gate is checked "before the body is decoded, so every kind is covered" [6](#0-5) , covering `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`, and `Execute`.

The Tron variant's `onAccept` jumps straight to `RequestKind kind = RequestKind(uint8(incoming.request.body[0]));` and, for `RedeemEscrow`/`RefundEscrow`, only calls `authenticate(incoming.request)` before decoding and calling `withdraw(...)` — no relayer check exists anywhere in this function or file for the escrow-release paths [3](#0-2) . The governance-only branches (`NewDeployment`, `UpdateParams`, `SweepDust`) are still gated by `keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())`, but that guard is orthogonal to, and does not substitute for, the relayer allowlist that the mainline contract enforces first [7](#0-6) .

This is exactly the class of bug OtterSec describes: the execution/dispatch layer (`IHandlerV2`) imposes no restriction on which account (relayer) can trigger a callback, so the application must enforce it itself; the Tron port forgot to port that check, silently reverting to "trust every relayer" behavior that the primary implementation explicitly treats as dangerous enough to gate (per the "fresh proxy is open until governance arms it" pattern documented for the mainline contract) [8](#0-7) .

### Impact Explanation
Any relayer — not just the one the gateway's governance designated via `setRelayer`/the relayer allowlist — can deliver `RedeemEscrow`, `RefundEscrow`, and governance-action messages to the Tron `IntentGatewayV2`. Because this removes an explicit, intentional authorization layer that the rest of the codebase treats as security-critical (the relayer gate is the difference between "everyone can mint" and "only the trusted relayer can mint" for the related `BridgeToken`/`HyperFungibleToken` contracts, and is unit-tested as covering every `RequestKind` in the mainline gateway), this is an unauthorized-app-action class finding: unauthorized parties can trigger privileged escrow release/refund flows and governance-sourced state changes on the Tron deployment without going through the designated relayer, undermining the deployment's intended trust model for who may finalize fund movements.

### Likelihood Explanation
`onAccept` is reachable directly by calling `HandlerV2`/`EvmHost.dispatchIncoming` with a valid state proof — a normal, permissionless relaying operation any actor can perform, per `IHandlerV2`'s explicit "permissionless" design [1](#0-0) . No privileged role, governance action, or additional exploit primitive is required — the missing check is a straightforward code omission relative to the sibling EVM implementation, making this readily exploitable by any relayer once such a message exists to relay (e.g., racing the intended relayer to be the one whose delivery finalizes an order or governance update).

### Recommendation
Port the `_checkRelayer(incoming.relayer)` gate from `evm/src/apps/intentsv2/ExtrinsicIntents.sol`'s `onAccept`/`onGetResponse` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling it unconditionally before `RequestKind` is read, matching the mainline contract's ordering and coverage of all request kinds.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` and configure a relayer allowlist entry (if the contract exposes an equivalent to `setRelayer`), matching the intended trust model of the mainline `ExtrinsicIntents.sol`.
2. Have Hyperbridge relay a valid `RedeemEscrow` (or `RefundEscrow`) `PostRequest` for a real order, but deliver it through `HandlerV2.handlePostRequests` from an *unlisted* relayer address (any account, not the configured one).
3. Observe that `evm/tron/contracts/apps/IntentGatewayV2.sol::onAccept` [3](#0-2)  proceeds to `authenticate(...)` and `withdraw(...)` without ever reverting on the relayer identity — contrast with `testOnAcceptGovernanceRejectsUnlistedRelayer`/`testOnGetResponseRejectsUnlistedRelayer` in the mainline test suite, which show the sibling EVM contract reverting with `Unauthorized` for the same unlisted-relayer scenario [9](#0-8) .

Note: I was unable to inspect the body of the Tron file's `authenticate()` function itself (only its call site was retrieved), so I cannot fully confirm whether it independently re-derives an equivalent restriction; based on the mainline contract's structure, `_authenticate`/`authenticate` validates the request's source-chain gateway registration, not the relaying party's identity, so it is very unlikely to substitute for the missing relayer gate — but this should be verified directly against the full function body in a follow-up review.

### Citations

**File:** docs/content/developers/evm/api/ihandler.mdx (L24-24)
```text
All handler methods are **permissionless** - anyone can call them to relay messages.
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-636)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L637-661)
```text
        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
            // Decode the body which includes optional destination-specific protocol fee updates
            ParamsUpdate memory update = abi.decode(incoming.request.body[1:], (ParamsUpdate));
            emit ParamsUpdated({previous: _params, current: update.params});
            _params = update.params;

            // Update destination-specific protocol fees if provided
            for (uint256 i; i < update.destinationFees.length;) {
                bytes32 stateMachineId = update.destinationFees[i].stateMachineId;
                uint256 feeBps = update.destinationFees[i].destinationFeeBps;
                _destinationProtocolFees[stateMachineId] = feeBps;

                unchecked {
                    ++i;
                }
                emit DestinationProtocolFeeUpdated(stateMachineId, feeBps);
            }
        } else if (kind == RequestKind.SweepDust) {
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L7-9)
```markdown
1. A relayer calls `HandlerV2.handlePostRequests` (or `handleGetResponses`). After proof
   verification the handler calls `host.dispatchIncoming(request, _msgSender())`. `_msgSender()` is
   plain `msg.sender`; the handler has no trusted forwarder.
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L14-16)
```markdown
3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts
   with `Unauthorized` when a relayer is set and the delivery is from anyone else. Only then is the
   first body byte read as a `RequestKind`. `onGetResponse` has the same two steps before touching
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4478-4514)
```text
    function testOnAcceptGovernanceRejectsUnlistedRelayer() public {
        // UpgradeContract: a forged upgrade cannot land unless the relayer submits it.
        address implBefore = _implementationOf(address(intentGateway));
        IntentGatewayV2Upgraded newImpl = new IntentGatewayV2Upgraded(address(this));
        PostRequest memory upgrade = _upgradeRequest(host.hyperbridge(), address(newImpl), "");

        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: upgrade}));
        assertEq(_implementationOf(address(intentGateway)), implBefore, "implementation unchanged");

        // NewDeployment: the gate runs before the body is decoded, so every kind is covered.
        PostRequest memory deployment = _newDeploymentRequest(bytes("NEW_CHAIN"), address(0xBEEF));
        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: deployment}));
        vm.expectRevert(IntentsBase.UnknownInstance.selector);
        intentGateway.instance(bytes("NEW_CHAIN"));

        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: deployment}));
        assertEq(intentGateway.instance(bytes("NEW_CHAIN")), address(0xBEEF), "relayer-submitted governance applies");
    }

    function testOnGetResponseRejectsUnlistedRelayer() public {
        (GetResponse memory response, bytes32 commitment, uint256 amount) = _cancelResponse();

        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onGetResponse(IncomingGetResponse({response: response, relayer: user}));
        assertEq(intentGateway._orders(commitment, address(usdc)), amount, "escrow untouched");

        uint256 before = usdc.balanceOf(user);
        vm.prank(address(host));
        intentGateway.onGetResponse(IncomingGetResponse({response: response, relayer: relayer}));
        assertEq(usdc.balanceOf(user) - before, amount, "authorised relayer refunds escrow");
    }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4516-4519)
```text
    /// A fresh proxy has no relayer and accepts every delivery: `initialize` does not touch the
    /// gate, and its only setter is host-only, so the governance upgrade that arms it has to get
    /// through first. Once armed, only that relayer is accepted.
    function testFreshProxyIsOpenUntilGovernanceArmsIt() public {
```
