### Title
Tron `IntentGatewayV2.onAccept` is missing the relayer allowlist gate present in the EVM `ExtrinsicIntents.onAccept`, letting any relayer trigger escrow release, refunds, and governance actions - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The EVM `IntentGatewayV2`/`ExtrinsicIntents.onAccept` (via `HyperApp`) enforces a single-relayer allowlist (`_checkRelayer(incoming.relayer)`) before decoding or acting on any incoming ISMP delivery, added specifically as a security control on 2026-09-03. The Tron fork of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements the identical `onAccept` dispatch logic (RedeemEscrow/RefundEscrow/NewDeployment/UpdateParams/SweepDust) but never received this gate: there is no `_relayer` state, no `setRelayer`, and no `_checkRelayer` call anywhere in the file. This is exactly the "normal path enforces a check, alternate path skips it" bug class described in the CVE-2026-88005 report, applied to Hyperbridge's intent-escrow settlement path instead of OAuth login.

### Finding Description
On the canonical EVM implementation, `onAccept` runs the relayer check before touching the request body: [1](#0-0) 

and the design decision for this gate is documented explicitly as a defense against unauthorized delivery: [2](#0-1) 

The Tron variant implements the same `RequestKind` dispatch (`RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`) but goes straight into `authenticate()` and body decoding with no relayer check at all: [3](#0-2) 

A grep of the Tron file confirms `_checkRelayer`, `_relayer`, `setRelayer`, and `relayer()` are entirely absent from it, whereas they are the load-bearing gate on every other sibling app contract (`ExtrinsicIntents.sol`, `BridgeToken.sol`, `HostManager.sol`) that received the same 2026-09-03 hardening pass.

`authenticate()` in the Tron contract only checks that `request.from`/`request.source` match a registered peer instance: [4](#0-3) 

This is a necessary but, per the project's own stated design, *insufficient* check on its own — the EVM gateway treats the relayer allowlist as an additional required layer on top of `authenticate`/`onlyHost`, and its absence on Tron reopens the exact class of unauthorized-delivery risk the 2026-09-03 patch was written to close.

### Impact Explanation
Any relayer able to get a valid ISMP delivery through `EvmHost.dispatchIncoming` on the Tron deployment (which is the intended, permissionless multi-relayer model that the EVM gateway deliberately narrowed to a single trusted relayer) can trigger `RedeemEscrow`/`RefundEscrow` withdrawals of user-escrowed funds, and — more critically — `UpdateParams`, `SweepDust`, and `NewDeployment` governance-equivalent actions, without the authorization step the rest of the protocol now requires. This is a concrete unauthorized-app-action / fund-drain risk on the escrow and dust-sweep paths, mirroring the medium-severity impact of the OAuth analog (an alternate code path bypassing an access-control check enforced on the primary path).

### Likelihood Explanation
Likelihood is high for any Tron deployment of this contract: no configuration or attacker precondition beyond being able to relay/deliver a message through the standard HandlerV2/host flow is required, since the missing gate is unconditional (there's no code path, flag, or state that re-enables it). This is a pure code-parity gap between the audited/hardened EVM contract and its Tron counterpart.

### Recommendation
Port the `_relayer`/`_checkRelayer`/`setRelayer`/`RelayerUpdated` mechanism from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` (and its `IntentsBase.sol` interface additions) into `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling `_checkRelayer(incoming.relayer)` as the first statement in `onAccept` and `onGetResponse`, before `authenticate()`/body decoding, exactly as done on the EVM side, and add regression tests mirroring `IntentGatewayV2Test.sol`'s `testOnAcceptRejectsUnlistedRelayer` for the Tron contract.

### Proof of Concept
1. Deploy `evm/tron/contracts/apps/IntentGatewayV2.sol` with escrowed orders present (identical setup to `evm/tests/foundry/IntentGatewayV2Test.sol`'s `_escrowedRedeemRequest`).
2. Have any relayer (not a designated/trusted one — there is none configurable) submit a valid ISMP `RedeemEscrow` delivery through the host/handler.
3. `onAccept` (lines 629-636) calls `authenticate()` and `withdraw()` directly with no relayer check, releasing escrowed tokens to the attacker-chosen beneficiary — compare against `testOnAcceptRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol` (lines 4461-4476), which shows the EVM contract reverts with `Unauthorized` for the same scenario until the correct relayer submits it.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L292-300)
```text
    /**
     * @dev Checks that the request originates from a known instance of the IntentGateway.
     */
    function authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        // IntentGateway only accepts incoming assets from itself or known instances
        if (instance(request.source) != module) revert Unauthorized();
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
