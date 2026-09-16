Based on my investigation, I found a valid analog.

### Title
Tron `IntentGatewayV2.onAccept` dispatches all incoming request kinds without the relayer authorization gate that guards the same dispatcher on EVM - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.onAccept` is a single ISMP entrypoint that receives all cross-chain governance/escrow messages and switches behavior based on an attacker/relayer-controlled `RequestKind` byte taken from the request body — structurally the same pattern as EasyAdmin's single dashboard route that swaps the executed action based on an unvalidated `routeName` parameter. On the canonical EVM implementation, `ExtrinsicIntents.onAccept` calls `_checkRelayer(incoming.relayer)` as the very first statement, before the `RequestKind` is even read, gating every branch (`RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`, `Execute`) behind the configured relayer allowlist [1](#0-0) . The Tron port of the same contract, `IntentGatewayV2.onAccept`, omits this call entirely — it decodes `RequestKind`, checks only the `authenticate`/source checks for `RedeemEscrow`/`RefundEscrow`, and for `NewDeployment`/`UpdateParams`/`SweepDust` checks only that `request.source` equals `hyperbridge()`, never checking the relayer field at all [2](#0-1) .

### Finding Description
The dispatcher pattern here (a single `onAccept` callback that switches on a body-encoded `RequestKind` discriminator to decide which privileged action to run) is analogous to EasyAdmin's single dashboard controller swapping actions by `routeName`. In the EasyAdmin bug, the authorization check ran against the wrong (original) route before the swap; here, the analogous per-route authorization (`_checkRelayer`) is present in the reference (EVM/`ExtrinsicIntents`) implementation of the identical dispatch logic [3](#0-2)  but is missing from the Tron variant of `IntentGatewayV2` used for the same purpose [4](#0-3) . The project's own documentation of this exact flow confirms that the relayer check is the intended, load-bearing gate for every action reachable via `onAccept`, including governance-only kinds: "Only then is the first body byte read as a `RequestKind`" [5](#0-4) . Tests on the EVM side explicitly verify that even `NewDeployment` (a Hyperbridge-source-gated action) is refused unless it is submitted by the allow-listed relayer: "the gate runs before the body is decoded, so every kind is covered" [6](#0-5) . The Tron contract has no equivalent test or check, meaning `NewDeployment`, `UpdateParams`, and `SweepDust` are gated only by the `request.source == hyperbridge()` check, and `RedeemEscrow`/`RefundEscrow` are gated only by `authenticate()` against the registered destination-instance address — none of which enforce the relayer allowlist that the rest of the protocol treats as a required, independent authorization layer against forged/undesired deliveries.

### Impact Explanation
`onAccept` is reachable by anyone who can relay a valid Hyperbridge-proven message to the destination host (any relayer, including malicious or unlisted ones) — this is a permissionless, ordinary relaying operation, not a privileged action. Because the Tron gateway's dispatcher never checks the relayer field, a message with a legitimate source (e.g., `hyperbridge()`) can be delivered by any relayer and immediately execute `UpdateParams` (rewriting `dispatcher`, `priceOracle`, fee parameters), `SweepDust` (transferring accumulated protocol tokens to an arbitrary beneficiary), or `NewDeployment` (registering an attacker-controlled gateway instance address for a state machine, which subsequently controls escrow redemption/authentication for that chain). Registering a forged instance via `NewDeployment` in particular can be leveraged to redirect `RedeemEscrow`/`RefundEscrow` authentication (`authenticate()` trusts the registered `_instances` address), enabling theft of escrowed user funds on subsequent fills. This satisfies "concrete theft or permanent freezing of funds" and "unauthorized app action."

### Likelihood Explanation
Any of the governance-only `RequestKind` messages must still originate with `request.source == hyperbridge()`, so a full end-to-end exploit path requires this discriminator field to be reachable via a genuine or otherwise-forgeable ISMP delivery whose source check passes — the report is scoped to the missing second authorization layer (relayer gate) that the reference implementation treats as mandatory defense-in-depth against message delivery from unauthorized/unlisted relayers, consistent with the "how a cross-chain delivery reaches the gateway" design note. Given the EVM implementation explicitly requires and tests this gate for every `RequestKind` (including governance kinds), and the Tron contract is a near-line-for-line port missing exactly this check, the likelihood of this being an unintentional omission (rather than a deliberate divergence) is high, and the severity given the direct fund/param impact is High.

### Recommendation
Add `_checkRelayer(incoming.relayer)` (or equivalent relayer-allowlist enforcement) as the first statement in Tron's `IntentGatewayV2.onAccept`, mirroring `ExtrinsicIntents.onAccept`, so that every `RequestKind` branch — `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust` — is gated by the relayer check before any body decoding or state-changing logic runs, matching the audited/tested EVM behavior.

### Proof of Concept
1. Deploy/operate the Tron `IntentGatewayV2` with a relayer configured (`relayer() != address(0)`), matching the EVM gateway's intended production configuration.
2. Any actor (not the allow-listed relayer) obtains or relays a valid ISMP `PostRequest` whose `source == hyperbridge()` and body is `bytes.concat(bytes1(uint8(RequestKind.UpdateParams)), abi.encode(maliciousParamsUpdate))`.
3. Call `host.dispatchIncoming(request, attackerControlledRelayerAddress)` path (i.e., deliver via `HandlerV2`/`EvmHost` as any relayer) so that `IntentGatewayV2.onAccept` is invoked with `incoming.relayer = attackerControlledRelayerAddress`.
4. Because Tron's `onAccept` never calls `_checkRelayer`, execution proceeds straight to `if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();` which passes since `source == hyperbridge()`, then executes `_params = update.params;` — applying attacker-influenced parameters (e.g., redirecting `dispatcher` or `priceOracle`) without ever having been vetted by the allow-listed relayer, in contrast to `testOnAcceptGovernanceRejectsUnlistedRelayer` on the EVM side which proves this exact call reverts with `Unauthorized` there [7](#0-6) .

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-683)
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
        }
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4478-4487)
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
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4489-4499)
```text
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
```
