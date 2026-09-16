### Title
Missing relayer allowlist gate on Tron `IntentGatewayV2.onAccept` allows forged-consensus governance takeover of escrow funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Doccano CVE's root cause is that an unprivileged/attacker-controlled parameter (`model_attribs`) is trusted to select and drive privileged behavior without an authorization check on the caller. The direct analog in Hyperbridge is the `onAccept` discriminator-dispatch pattern (`request.body[0]` selects a `RequestKind`/`OnAcceptActions` and the decoded payload is then trusted). The EVM mainline hardened every such entry point (`ExtrinsicIntents.onAccept`, `HostManager.onAccept`, `SimplexPaymaster.onAccept`, `BandwidthManager.onAccept`) with a `_checkRelayer`/`restrict(...)` gate that runs *before* the discriminator byte is even read, precisely so a forged consensus proof relayed by an arbitrary account cannot drive governance actions. The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, was not updated with this gate.

### Finding Description
`IntentGatewayV2.onAccept` on Tron (`evm/tron/contracts/apps/IntentGatewayV2.sol:629-683`) only checks `onlyHost` before reading `RequestKind kind = RequestKind(uint8(incoming.request.body[0]))`: [1](#0-0) 

Compare this to the hardened EVM version, `ExtrinsicIntents.onAccept` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:330-350`), which calls `_checkRelayer(incoming.relayer)` immediately on entry, before the body is decoded at all: [2](#0-1) 

The relayer gate was added specifically because `onlyHost` alone is insufficient: `incoming.relayer` is only as trustworthy as `_hostParams.handler`, and a forged/compromised consensus proof lets *any* relayer deliver a message through the honest handler (see `sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md` and the "how a cross-chain delivery reaches the gateway" flow doc): [3](#0-2) 

The Tron `onAccept`'s `NewDeployment`, `UpdateParams`, and `SweepDust` branches accept `incoming.request.source` as authorization (checked via `keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())`), but that source field, like the relayer, is only as trustworthy as the consensus verification behind it — the exact "unprivileged parameter drives privileged action" bug class the CVE describes: [4](#0-3) 

Because there is no per-relayer allowlist, once a consensus proof is accepted (forged, buggy verifier, or malicious authority set on the Tron-side light client), an attacker who can produce or relay any message claiming to originate from "Hyperbridge" can drive `SweepDust` (sends all protocol dust, `beneficiary` attacker-controlled) or `UpdateParams` (rewrites `priceOracle`, fee params) with no independent relayer check — a control the EVM-mainline gateway already added as defense-in-depth for exactly this scenario.

### Impact Explanation
`SweepDust` sends attacker-controlled amounts of tokens to an attacker-controlled `beneficiary`: [5](#0-4) 
and `UpdateParams` can rewrite fee/oracle parameters used to price escrow releases. Combined with the missing relayer gate, this is a direct path to theft of escrowed/protocol funds if any single consensus-verification weakness or handler-swap ever occurs on the Tron deployment — the same "gate that exists for" scenario the EVM-side decision docs and tests (`testForgedHandlerSwapIsRefused`) explicitly defend against on EVM, but not on Tron.

### Likelihood Explanation
This requires a forged/compromised consensus proof or a compromised/malfunctioning handler to be accepted by the host — not a trivial precondition — matching the CVSS AC:H/PR:H profile of the referenced CVE. However, unlike the EVM-mainline contracts, Tron's `IntentGatewayV2` has zero secondary defense (no relayer allowlist) once that precondition is met, whereas the audited/hardened EVM path requires *both* a forged proof *and* passing the relayer allowlist.

### Recommendation
Port the relayer-allowlist gate (`_relayer`, `relayer()`, `setRelayer()`, `_checkRelayer` called first in `onAccept`/`onGetResponse`) from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` / `IntentsBase.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, matching the same "gate runs before the body is decoded" invariant, and add regression tests analogous to `testOnAcceptGovernanceRejectsUnlistedRelayer` for the Tron contract.

### Proof of Concept
1. Assume a forged/compromised consensus proof (or malicious handler swap) causes `EvmHost.dispatchIncoming` on the Tron deployment to call `IntentGatewayV2.onAccept` with a crafted `PostRequest` whose `source` bytes equal `IDispatcher(host()).hyperbridge()`.
2. Body: `bytes.concat(bytes1(uint8(RequestKind.SweepDust)), abi.encode(SweepDust({beneficiary: attacker, outputs: [...]})))`.
3. `onlyHost` passes (call genuinely comes from the host); the source check passes because the forged proof lets the attacker set `request.source`.
4. No relayer check exists, so `_instances`/no allowlist rejects the delivery — dust is swept directly to `attacker`, unlike the EVM-mainline gateway which would additionally revert with `Unauthorized` from `_checkRelayer` for any non-allowlisted relayer (see `testOnAcceptGovernanceRejectsUnlistedRelayer`, `evm/tests/foundry/IntentGatewayV2Test.sol:4478-4500`). [6](#0-5)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-681)
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
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
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

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md (L5-9)
```markdown
The app gates check an address the host reports, and the host takes it from its handler. The
handler is a host parameter that a `SetHostParam` governance message can replace, and until now
any relayer could deliver that message once its consensus proof verified. Under a forged consensus
an attacker would swap in a handler that reports the whitelisted relayer on every message, and the
app gates would pass. Gating the HostManager closes that route.
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
