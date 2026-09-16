### Title
Tron `IntentGatewayV2.onAccept` lacks the relayer-authorization gate the canonical EVM gateway enforces, allowing unauthorized escrow releases and governance actions - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron port of `IntentGatewayV2` (`evm/tron/contracts/apps/IntentGatewayV2.sol`) implements `onAccept` with only the `onlyHost` modifier and, for governance actions, a check that `request.source == hyperbridge()`. It never checks `incoming.relayer` against an authorized/allowlisted relayer anywhere in the function. This is the same class of bug as the reported mem0 issue (CWE-306): a state-mutating entry point (`PUT`-equivalent: escrow withdrawal, parameter updates, new-deployment registration, dust sweep) is missing an authorization check on the identity of the caller that is trusted to deliver the message.

### Finding Description
`onAccept` in the Tron gateway: [1](#0-0) 

```
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        authenticate(incoming.request);
        WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
        return withdraw(body, kind == RequestKind.RefundEscrow);
    }
    // only hyperbridge is permitted to perform these actions
    if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
    if (kind == RequestKind.NewDeployment) { ... }
    else if (kind == RequestKind.UpdateParams) { ... }
    else if (kind == RequestKind.SweepDust) { ... }
}
```

Compare to the canonical EVM implementation, documented and tested in `evm/tests/foundry/IntentGatewayV2Test.sol`, where the exact same governance actions (`UpgradeContract`, `NewDeployment`) are refused unless delivered by the specific relayer the gateway's governance armed: [2](#0-1) 

and where the delivery-path documentation explicitly states the relayer check is a required, separate gate sitting after `onlyHost` and before any body decoding: [3](#0-2) 

The `onlyHost` check alone is insufficient authorization by the project's own design: the flow doc explicitly notes "The address checked in step 3 is only as trustworthy as the contract in step 1" — i.e., `onlyHost` only proves the message came through *some* handler; the relayer check is the defense that stops a forged/compromised handler (exactly the `MaliciousHandler` scenario exercised in `evm/tests/foundry/HostManagerTest.sol`) from injecting an attacker-chosen relayer identity and having it accepted as authoritative: [4](#0-3) 

The Tron contract's `onAccept` never performs this second check for any of its four actions (`RedeemEscrow`/`RefundEscrow` via `authenticate`, and `NewDeployment`/`UpdateParams`/`SweepDust` via only the source check), so the relayer field carried in `IncomingPostRequest` is read nowhere in this function.

### Impact Explanation
If the trusted handler ever reports an unauthorized relayer for a delivered message (the same failure mode the `MaliciousHandler`/`HostManager` gate exists to prevent), the Tron gateway will still execute:
- `SweepDust` — transfers accumulated protocol dust to an attacker-chosen beneficiary.
- `NewDeployment` — overwrites the trusted `_instances[chain]` gateway address, which controls where future escrow releases and withdrawal-request validations route, enabling redirection of funds on subsequent fills/withdrawals.
- `UpdateParams` — rewrites protocol fee parameters.
- `RedeemEscrow`/`RefundEscrow` — releases escrowed user funds to a beneficiary named in the request body, with no relayer-based defense-in-depth.

This is a direct "unauthorized app action" / freezing-or-redirection-of-funds vector on the Tron deployment, matching the Validate criteria (unauthorized app action / unsound state commitment) reachable from a single relayed message through `HandlerV2`/`EvmHost`-equivalent dispatch on Tron.

### Likelihood Explanation
Exploitation requires the handler (or the honest delivery path) to report a relayer address other than the one governance intends to trust — the same precondition the `HostManager`/mainline gateway gate exists specifically to defend against (compromised/forged handler, or a handler bug in the Tron chain's message-verification layer). Given the mainline EVM contract and its test suite (`IntentGatewayV2Test.sol`, `HostManagerTest.sol`) treat this as a real, tested threat model worth defending against, its absence in the Tron variant is a genuine regression/gap rather than a theoretical concern, and it is reachable by any relayer/whoever controls delivery on the Tron side without any privileged action from the user.

### Recommendation
Add the same relayer-authorization check (`_checkRelayer(incoming.relayer)` or equivalent) used by the canonical `IntentGatewayV2`/`ExtrinsicIntents` implementation to the Tron `onAccept`, before decoding any `RequestKind`, for both the escrow paths (`RedeemEscrow`/`RefundEscrow`) and the governance paths (`NewDeployment`, `UpdateParams`, `SweepDust`). Add regression tests mirroring `testOnAcceptGovernanceRejectsUnlistedRelayer` and `testOnGetResponseRejectsUnlistedRelayer` from `evm/tests/foundry/IntentGatewayV2Test.sol` to the Tron test suite.

### Proof of Concept
1. Handler/host delivers a `PostRequest` with `body[0] = RequestKind.SweepDust` (or `NewDeployment`/`UpdateParams`) and `incoming.relayer = attacker`.
2. `onAccept` passes `onlyHost` (delivery came through the configured handler) and, for `SweepDust`/`NewDeployment`/`UpdateParams`, only checks `request.source == hyperbridge()` — it never inspects `incoming.relayer`.
3. The action executes unconditionally, e.g. dust is swept to `req.beneficiary` chosen by whoever crafted the request body, or `_instances[chain]` is overwritten — with no verification that `attacker` was an authorized relayer for governance delivery.

Note: I was unable to retrieve the full body of the `authenticate(...)` helper (`evm/tron/contracts/apps/IntentGatewayV2.sol`) before running out of tool iterations, so I cannot confirm with certainty whether it additionally validates `incoming.relayer` internally. The `onAccept` function signature and the governance branches (`NewDeployment`/`UpdateParams`/`SweepDust`), however, are confirmed to have no relayer check at all, which alone constitutes the missing-authorization analog described above. If `authenticate` also lacks a relayer check, the escrow paths are impacted equally.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L623-645)
```text
    /**
     * @notice Executes an incoming post request.
     * @dev This function is called when an incoming post request is accepted.
     * It is only accessible by the host.
     * @param incoming The incoming post request data.
     */
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
            // Decode the body which includes optional destination-specific protocol fee updates
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4478-4500)
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
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L14-21)
```markdown
3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts
   with `Unauthorized` when a relayer is set and the delivery is from anyone else. Only then is the
   first body byte read as a `RequestKind`. `onGetResponse` has the same two steps before touching
   the response.

So a delivery from anyone but the authorised relayer never decodes the body, never runs
`_authenticate`, and leaves no receipt. The authorised relayer submitting the same message later
takes the normal path. A gateway whose `_relayer` is zero accepts every relayer: that is the state
```

**File:** evm/tests/foundry/HostManagerTest.sol (L27-37)
```text
/// @dev What an attacker would install as the host's handler: it passes the host's interface
/// check, verifies nothing, and reports whatever relayer address it is told to.
contract MaliciousHandler is ERC165 {
    function supportsInterface(bytes4 interfaceId) public view override returns (bool) {
        return interfaceId == type(IHandlerV2).interfaceId || super.supportsInterface(interfaceId);
    }

    function deliver(EvmHost host, PostRequest memory request, address claimedRelayer) external {
        host.dispatchIncoming(request, claimedRelayer);
    }
}
```
