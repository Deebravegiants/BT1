Confirmed: the Tron variant of `IntentGatewayV2.onAccept` (`evm/tron/contracts/apps/IntentGatewayV2.sol:629-660`) has no `_checkRelayer`/relayer-allowlist gate at all — unlike its EVM counterpart (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:330-350`), which calls `_checkRelayer(incoming.relayer)` before decoding anything. That EVM-side gate exists specifically to close the "forged consensus/handler swap injects an unauthorised relayer identity" bug class documented in `sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md` and `sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md`. The Tron contract still checks `onlyHost` and, for governance actions, that `request.source == hyperbridge`, but it never checks *who delivered* the message (`incoming.relayer`), so any relayer whose consensus/state proof passes `HandlerV2`/host verification can submit `NewDeployment`, `UpdateParams`, `SweepDust`, or (if present) upgrade/rotation-carrying governance bodies and have them applied.

### Title
Missing relayer allowlist check in Tron `IntentGatewayV2.onAccept` allows unauthorized governance-action injection - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron port of `IntentGatewayV2.onAccept` omits the `_checkRelayer` gate that the EVM implementation enforces on every delivery. This is the config-injection analog of CVE-2020-18875: an unprivileged relayer can get the gateway to accept and apply governance-class payloads (`NewDeployment`, `UpdateParams`, `SweepDust`) that the EVM codebase's own security model says must only be trusted from a single admin-configured relayer.

### Finding Description
On the EVM side, `ExtrinsicIntents.onAccept` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:330-350`) calls `_checkRelayer(incoming.relayer)` as the very first statement — before any decoding of `RequestKind` — so a delivery from any account other than the configured `_relayer` reverts with `Unauthorized`, regardless of whether the underlying consensus proof verified. [1](#0-0) 

The Tron contract's `onAccept` (`evm/tron/contracts/apps/IntentGatewayV2.sol:629-660`) has only `onlyHost` and, for the governance branch, a `request.source == hyperbridge` check — it never calls anything analogous to `_checkRelayer`/`_authenticate` against `incoming.relayer`: [2](#0-1) 

The design docs explain exactly why this gate exists and is load-bearing: the relayer address the app checks is only as trustworthy as `EvmHost.dispatchIncoming`'s caller-supplied `relayer` param, which ultimately traces back to a value a compromised/forged consensus update (via a swapped handler) could manipulate; the relayer allowlist at the app layer is the second, independent line of defense against that. [3](#0-2)  The changelog documenting when this protection was added to the EVM gateway confirms it is a deliberate, security-motivated control and not incidental: [4](#0-3) 

### Impact Explanation
Without the relayer check, any account capable of getting a valid state/consensus proof accepted by the host handler (i.e., any permissionless relayer relaying a legitimate cross-chain message, or — in the threat model this gate was built for — an attacker exploiting a weaker/forged consensus path) can submit `UpdateParams` to rewrite the gateway's fee/oracle/dispatcher parameters and per-destination protocol fees, `NewDeployment` to register an attacker-controlled peer "gateway" instance for an arbitrary state machine (which is subsequently trusted by `authenticate()` for `RedeemEscrow`/`RefundEscrow`), or `SweepDust` to drain accumulated dust/token balances to an arbitrary beneficiary — all without the single authorised relayer's involvement. Registering a malicious `NewDeployment` instance is particularly severe: subsequent `RedeemEscrow` requests "from" that forged instance would pass `authenticate()` and release escrowed user funds to an attacker-chosen beneficiary, i.e., theft of escrowed funds.

### Likelihood Explanation
Reachable from a single relayed/dispatched cross-chain message once the source-check (`request.source == hyperbridge`) is satisfied. On the EVM side this is treated as a real, actively-defended attack surface (see the changelog and flow doc above), which strongly suggests the same class of message can originate from an unprivileged or compromised relayer/consensus path in production. The missing check on Tron directly reintroduces the exact vulnerability the EVM side patched.

### Recommendation
Add the same `_checkRelayer`/relayer-allowlist gate used by `evm/src/apps/intentsv2/ExtrinsicIntents.sol` to the Tron `IntentGatewayV2.onAccept`, checking `incoming.relayer` against the contract's configured `_relayer` before any `RequestKind` is decoded or acted upon (covering `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, and `SweepDust` alike), matching the EVM implementation's ordering and semantics (including fail-open only while `_relayer == address(0)`, until governance arms it).

### Proof of Concept
1. Deploy/observe the Tron `IntentGatewayV2` proxy with `_relayer` set to the authorised relayer address (armed state), mirroring the EVM setup in `evm/tests/foundry/IntentGatewayV2Test.sol`.
2. Craft a `PostRequest` with `source == host.hyperbridge()`, `to == address(intentGateway)`, and body `bytes.concat(bytes1(uint8(RequestKind.NewDeployment)), abi.encode(Deployment{stateMachineId: <attacker-chosen>, gateway: <attacker address>}))`.
3. Have the host deliver it via `dispatchIncoming(request, relayer=<any unauthorised address>)` (i.e., not the configured `_relayer`).
4. Because Tron's `onAccept` never checks `incoming.relayer`, the call proceeds past `onlyHost`, passes the `source == hyperbridge` check, and registers the attacker's `Deployment`/gateway instance — whereas the equivalent EVM test (`testOnAcceptGovernanceRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol:4478-4500`) shows the EVM contract reverts with `Unauthorized` for the identical unauthorised-relayer delivery. [5](#0-4)

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-340)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-660)
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
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L24-31)
```markdown
The address checked in step 3 is only as trustworthy as the contract in step 1, and that contract
is `_hostParams.handler`, which `HostManager.onAccept` can replace through a `SetHostParam`
request from Hyperbridge (`evm/src/core/HostManager.sol`, then `EvmHost.updateHostParams`). The
HostManager therefore runs the same relayer check before decoding any governance action, against
its admin: the account named in its constructor, which is also the only one allowed to bind the
host with `init` when the host was not known at construction. `testForgedHandlerSwapIsRefused` in
`evm/tests/foundry/HostManagerTest.sol` plays the swap through the real host and shows it refused.
The HostManager sees no user traffic, so this leaves ordinary relaying open.
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
