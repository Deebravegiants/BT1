### Title
Missing per-app relayer authorization on Tron `IntentGatewayV2.onAccept` allows any relayer to forge governance and escrow actions - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron deployment of `IntentGatewayV2` (`evm/tron/contracts/apps/IntentGatewayV2.sol`) never received the relayer-allowlist authorization fix that was applied to the canonical EVM gateway (`evm/src/apps/intentsv2/ExtrinsicIntents.sol`). `onAccept` is gated only by `onlyHost`, with no `_checkRelayer`/`_relayer` check, so any relayer who can get a message delivered through the host (including one that only barely passes consensus/handler checks) can drive escrow redemption/refund, register a new `NewDeployment` gateway peer, or rewrite `UpdateParams`/`SweepDust`.

### Finding Description
On the canonical EVM path, `ExtrinsicIntents.onAccept` runs `onlyHost` and then immediately `_checkRelayer(incoming.relayer)` before reading any byte of the body: [1](#0-0) 
`_checkRelayer` enforces that once `_relayer` is set, only that address's deliveries are honored: [2](#0-1) 
This gate was deliberately added (2026-09-03 changelog) specifically because it protects "escrow redemptions, refunds and every governance action" from a delivery submitted by an unauthorized relayer: [3](#0-2) 

The Tron contract implements the same `onAccept` dispatch surface (`RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`) but is missing this check entirely — it is gated only by `onlyHost`, with no `_relayer`/`_checkRelayer`/`RelayerUpdated` symbols anywhere in the file: [4](#0-3) [5](#0-4) 

This is structurally the same bug class as the reported GitLab issue: a governance/config-modifying action (there, protected-branch config; here, `UpdateParams`/`NewDeployment`/escrow settlement) is reachable through an API/dispatch path that omits an authorization check present and required elsewhere in the same code family, letting an actor without the intended privilege (here, any relayer, not the designated one) perform the privileged action.

### Impact Explanation
Once a message is dispatched to the Tron gateway's `onAccept` — which only requires arriving through the local `host` (i.e., passing consensus/state-proof verification on the delivery batch, not passing any per-app relayer allowlist) — any relayer can:
- Trigger `RedeemEscrow`/`RefundEscrow` (subject only to `authenticate()`, which checks the source module address, not the delivering relayer) to redirect escrowed funds.
- Trigger `NewDeployment` to register an attacker-controlled address as a trusted peer gateway for an arbitrary state machine, which is subsequently trusted by `authenticate()` for future escrow redemptions/refunds from that "chain" — a foothold for forging settlement messages.
- Trigger `UpdateParams` to rewrite `_params` (host, dispatcher, fee, price oracle, solver-selection toggle) and per-destination protocol fees.
- Trigger `SweepDust` to redirect swept native/token balances to an attacker beneficiary.

This is concrete theft/permanent-fund-risk: forged/unauthorized settlement and forged trusted-peer registration on the intents flow, matching the "forged message delivery" / "unauthorized app action" acceptance criteria.

### Likelihood Explanation
Reachability requires only that a message be delivered to the Tron `IntentGatewayV2` through its host — the relayer submitting/proving that delivery does not need to be any privileged/whitelisted actor, since the per-app relayer gate that exists on the sibling EVM implementation is absent here. Any of Hyperbridge's own governance-originated messages (`NewDeployment`, `UpdateParams`, `SweepDust` are already source-restricted to the Hyperbridge parachain) are protected against forged *source*, but not against which *relayer* is allowed to deliver them, and `RedeemEscrow`/`RefundEscrow` have no source restriction beyond the peer-gateway `authenticate()` check. The security team explicitly identified and closed this exact class of issue in the primary EVM contract on 2026-09-03; the Tron variant appears to be an out-of-sync fork that missed the fix.

### Recommendation
Port the `_relayer` / `setRelayer` / `_checkRelayer` gate from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` (and `IntentsBase.sol`) into `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling `_checkRelayer(incoming.relayer)` (and the equivalent for `onGetResponse`, if present) immediately after `onlyHost` and before any body decoding, mirroring the audited EVM gateway exactly so the Tron deployment is not left as an unpatched fork.

### Proof of Concept
1. Deploy/observe the Tron `IntentGatewayV2` contract as configured today (no `_relayer` state exists).
2. Have any relayer (not a designated/whitelisted one — since none can be designated at all) submit a valid ISMP delivery through the Tron host's handler so that `host.dispatchIncoming` calls `IntentGatewayV2.onAccept` with an `IncomingPostRequest` whose `body[0] == RequestKind.NewDeployment` and `source == hyperbridge` (satisfying the only check present at line 638).
3. `onAccept` decodes `NewDeployment` and sets `_instances[keccak256(body.stateMachineId)] = body.gateway` to an attacker-controlled address, with no check on which relayer delivered the message: [6](#0-5) 
4. The attacker-controlled "peer gateway" is now trusted by `authenticate()` for that state machine, allowing forged `RedeemEscrow`/`RefundEscrow` messages purportedly "from" that chain to pass the from/source check and redeem real escrowed user funds to an attacker-chosen beneficiary.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L623-683)
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
