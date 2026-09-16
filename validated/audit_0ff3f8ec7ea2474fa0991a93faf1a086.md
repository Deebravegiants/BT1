### Title
Tron `IntentGatewayV2.onAccept`/`onGetResponse` omit the relayer allowlist gate present on the audited EVM gateway, removing the defense-in-depth against a forged-handler delivery - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The mainline EVM `IntentGatewayV2`/`ExtrinsicIntents` was hardened on 2026-09-03 to reject `onAccept` and `onGetResponse` deliveries from any relayer but a single allowlisted `_relayer`, checked before the request body is even decoded [1](#0-0) [2](#0-1) . The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, has no `_relayer` state, no `_checkRelayer`, and no `onlyHost`-adjacent relayer check anywhere in the file [3](#0-2) [4](#0-3) . It only checks `onlyHost` plus a source-instance check (`authenticate`/hyperbridge-source), exactly the two checks the 2026-09-03 fix decided were insufficient by themselves.

### Finding Description
On the audited EVM path, `onAccept` runs `_checkRelayer(incoming.relayer)` immediately, before the request kind byte is even read, so every action — escrow redemption, refund, `NewDeployment`, `UpdateParams`, `SweepDust`, and `Execute` (which delegatecalls the implementation and can reach `upgradeToAndCall`) — is gated on a single allowlisted relayer address [5](#0-4) . `onGetResponse` carries the same gate [6](#0-5) .

The stated rationale for this gate is documented directly: the app-level source check alone is not sufficient because the host's `handler` — the contract that reports the relayer address to the app on delivery — is itself a host parameter that a `SetHostParam` governance message can replace; a forged consensus proof could swap in a malicious handler that reports the whitelisted relayer (or any address the app happens to trust) on every message, defeating any check keyed only on `incoming.relayer` as reported by that handler path [7](#0-6) . Gating the app itself on an allowlisted relayer is the second layer of defense the Hyperbridge team added on top of `HostManager`'s own gating, specifically so that IntentGatewayV2's escrow-moving code cannot be driven by an arbitrary relayer even if the handler/consensus layer is compromised.

Tron's `IntentGatewayV2.onAccept` has no equivalent of `_checkRelayer` at all:
```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        authenticate(incoming.request);
        WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
        return withdraw(body, kind == RequestKind.RefundEscrow);
    }
    // only hyperbridge is permitted to perfom these actions
    if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
    ...
``` [8](#0-7) 

and `onGetResponse` releases escrow purely on `onlyHost` plus a storage-proof emptiness check, with no relayer check whatsoever:
```solidity
function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
    if (incoming.response.values[0].value.length != 0) revert Filled();
    WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
    withdraw(body, true);
}
``` [4](#0-3) 

A grep of the Tron package confirms `_relayer`, `_checkRelayer` and any relayer allowlist are absent from the entire directory . This is the same shape of bug as the Reconmap report: a control that the rest of the system's authorization model relies on (`AllowAnonymous` vs. the fallback policy in Reconmap; the relayer allowlist vs. `onlyHost`+source-check here) was simply never applied on one code path, even though the surrounding design explicitly assumes it is present as a second line of defense.

### Impact Explanation
`onAccept`'s `RedeemEscrow`/`RefundEscrow` branches and `onGetResponse` directly call `withdraw`, which transfers escrowed ERC20/native tokens and accumulated fees to `body.beneficiary` [9](#0-8) . With the relayer allowlist missing, the sole barrier between an attacker and draining every intent's escrow on the Tron gateway is the `onlyHost` + source/instance check — precisely the layer the EVM team judged insufficient once a handler-swap or forged-consensus path exists, since a compromised or misconfigured handler can make `incoming.relayer` (or, here, simply the absence of any relayer check) irrelevant to who actually triggers the withdrawal. The governance branches (`NewDeployment`, `UpdateParams`, `SweepDust`) are equally unprotected beyond the hyperbridge-source check, so the same failure mode can reconfigure destination-fee parameters, register a malicious peer gateway, or sweep dust to an attacker-chosen beneficiary.

### Likelihood Explanation
This is not reachable by a completely unauthenticated caller in the same trivial way as the Reconmap `AllowAnonymous` endpoint — it still requires a message to pass the host's `onlyHost` restriction (i.e., a state/consensus proof that the Tron host accepts). But it removes exactly the defense-in-depth layer that the project's own security decisions state is needed because the handler/consensus layer is not treated as unconditionally trustworthy on the EVM side; the same threat model applies to Tron's IntentGatewayV2 since it uses the identical `onlyHost`/`IDispatcher`/handler architecture. Given that the mainline EVM contract was patched for this exact class of gap, and the Tron port is a near-verbatim fork that never received the fix, this is a straightforward regression/parity gap rather than a novel exploit, making it a realistic and remediable finding rather than a purely theoretical one.

### Recommendation
Port the relayer-allowlist mechanism from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` / `IntentsBase.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`: add a `_relayer` slot, a `setRelayer`/governance-settable rotation path, and call `_checkRelayer(incoming.relayer)` at the top of both `onAccept` (before the `RequestKind` switch) and `onGetResponse`, mirroring the EVM implementation exactly so Tron's escrow-moving and governance code paths get the same second authorization layer.

### Proof of Concept
Not directly demonstrable from static analysis alone since exploitation depends on obtaining a delivery that passes Tron's `onlyHost` check with an attacker-controlled `beneficiary`/governance payload (e.g., via a compromised handler or forged proof, the same precondition the EVM fix's own test suite exercises in `evm/tests/foundry/IntentGatewayV2Test.sol`'s `testOnAcceptRejectsUnlistedRelayer`/`testSetRelayerToZeroReopensTheGate` tests [10](#0-9) ). Unlike the EVM gateway, replaying the same attack against the Tron contract cannot be blocked at the relayer-allowlist layer because that layer does not exist there — any `onAccept`/`onGetResponse` call that clears `onlyHost` and the source check unconditionally executes `withdraw` or the governance action, with no way to reject it based on which relayer delivered it.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-350)
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
        if (kind == RequestKind.NewDeployment) {
            _addDeployment(abi.decode(incoming.request.body[1:], (Deployment)));
        } else if (kind == RequestKind.UpdateParams) {
            _updateParams(abi.decode(incoming.request.body[1:], (ParamsUpdate)));
        } else if (kind == RequestKind.SweepDust) {
            _sweepDust(abi.decode(incoming.request.body[1:], (SweepDust)));
        } else if (kind == RequestKind.Execute) {
            Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:]);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-366)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-744)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
}
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4447-4476)
```text
    function testSetRelayerToZeroReopensTheGate() public {
        (PostRequest memory request,, uint256 amount) = _escrowedRedeemRequest();
        vm.prank(address(host));
        intentGateway.setRelayer(address(0));
        assertEq(intentGateway.relayer(), address(0));
        assertEq(intentGateway.version(), 2, "reopening the gate is not a migration either");

        // With no relayer set the gate is open, so a delivery from anyone lands.
        uint256 before = usdc.balanceOf(filler);
        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: request}));
        assertEq(usdc.balanceOf(filler) - before, amount, "open gate releases escrow");
    }

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
