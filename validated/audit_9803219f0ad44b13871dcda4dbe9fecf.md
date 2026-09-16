### Title
Tron `IntentGatewayV2` lacks the relayer allowlist gate applied to the EVM gateway, allowing an unauthorized relayer to trigger escrow redemption/refund via a forged consensus path - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The mainline EVM `IntentGatewayV2`/`ExtrinsicIntents` enforces a relayer allowlist (`_checkRelayer`) on both `onAccept` and `onGetResponse`, checked before the message body is even decoded, specifically to close a route where a forged consensus/handler swap could let an arbitrary relayer trigger escrow release, refunds, and governance actions. [1](#0-0) [2](#0-1)  The Tron deployment's copy of this same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements `onAccept` and `onGetResponse` without any relayer check at all — only the `authenticate()` (source-gateway) check on the redeem/refund path and a Hyperbridge-source check on governance actions, with `onGetResponse` performing no relayer or source authentication whatsoever before calling `withdraw()`. [3](#0-2) 

### Finding Description
This is the same bug class as the External Report: two code paths guard the same privileged action (releasing escrowed funds via `withdraw()`), but only one of them enforces the authorization control the protocol relies on. In the EVM `ExtrinsicIntents.onAccept`/`onGetResponse`, `_checkRelayer(incoming.relayer)` is the first statement, rejecting any delivery not from the single allowlisted relayer before the body is decoded or `withdraw` is reached. [4](#0-3) [5](#0-4)  This gate exists precisely because the relayer identity forwarded to `onAccept`/`onGetResponse` originates from `EvmHost.dispatchIncoming`'s `relayer` argument, which is only as trustworthy as the host's registered `handler` — a parameter that governance (`SetHostParam`) can swap, and which a forged consensus proof could exploit to make an arbitrary relayer appear authorized. [6](#0-5) 

The Tron `IntentGatewayV2.onAccept` performs `authenticate(incoming.request)` (verifying `request.from` matches the registered peer gateway address) for `RedeemEscrow`/`RefundEscrow`, but has no `_checkRelayer` equivalent anywhere in the file. [7](#0-6)  Its `onGetResponse` is worse: it has neither a relayer check nor a source/peer authentication check — it only verifies the response's storage-proof value is empty before calling `withdraw()` directly. [8](#0-7)  Because `withdraw()` on Tron unconditionally transfers escrowed input tokens and fee-token balances to `body.beneficiary` decoded straight from the delivered message, [9](#0-8)  the Tron deployment reaches the exact fund-release logic the EVM side hardened, through a path (`onGetResponse`, and to a lesser degree `onAccept`) with strictly weaker authorization checks — a direct parallel to filebrowser's inconsistent enforcement between its "raw download" and "public share download" code paths.

### Impact Explanation
If the Tron host's handler/relayer reporting can be manipulated (the same forged-consensus/handler-swap scenario the EVM gate was built to close), an unauthorized party can deliver a crafted `onGetResponse` (or `onAccept` RedeemEscrow/RefundEscrow) message and drain escrowed input tokens and accumulated transaction fees from the Tron `IntentGatewayV2` to an attacker-chosen beneficiary, since no relayer allowlist restricts who may trigger `withdraw()` on that deployment. This is concrete theft of escrowed intent funds, matching "concrete theft ... of funds" and "unauthorized app action" in the validation criteria.

### Likelihood Explanation
Exploitation requires the same precondition the EVM fix's own design notes describe: control over what the host reports as the delivering relayer/handler (e.g., via a forged consensus proof or a compromised/malicious handler swap) — this is not a trivial, always-available attack, but it is exactly the threat the EVM-side gate was purpose-built to close on 2026-09-03. [2](#0-1)  Because the Tron contract was evidently not updated with this same hardening (the changelog's file list for the relayer-allowlist rollout does not include `evm/tron/contracts/apps/IntentGatewayV2.sol`), the Tron gateway remains in the pre-fix, weaker state indefinitely unless separately patched — making this a standing gap rather than a one-off oversight.

### Recommendation
Port the relayer-allowlist gate (`_relayer` storage slot, `_checkRelayer`, `setRelayer`) from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, and call `_checkRelayer` as the first statement in both `onAccept` and `onGetResponse`, before any body decoding or `withdraw()` call, mirroring the EVM implementation exactly. Audit any other Tron-specific or otherwise divergent contract copies (host manager, other app gateways) for the same drift against their EVM counterparts, since this class of bug recurs whenever a security fix is applied to one deployment target but not its duplicated/forked copy.

### Proof of Concept
Not independently executable from the index alone (Tron contracts and their exact deployment/host wiring are not fully available in this index), but the structural PoC is:
1. Compare `evm/src/apps/intentsv2/ExtrinsicIntents.sol` `onAccept`/`onGetResponse` (lines 330–366) against `evm/tron/contracts/apps/IntentGatewayV2.sol` `onAccept`/`onGetResponse` (lines 631–744) — the former calls `_checkRelayer(incoming.relayer)` unconditionally first; the latter never does.
2. Given a scenario where the host's reported relayer/handler is attacker-influenced (the documented "forged consensus swaps handler" scenario), craft a `GetResponse` whose `context` decodes to a `WithdrawalRequest` naming the attacker as beneficiary and whose `values[0].value` is empty.
3. Deliver it through the Tron host to `onGetResponse`; since there is no relayer or source check, `withdraw()` executes and transfers escrowed tokens/fees to the attacker.

Note: full verification of Tron's host/handler trust model and deployment status is limited by index coverage of `evm/tron/`; a Devin session with full repo access is recommended to confirm the Tron host's exact relayer-reporting semantics before treating this as conclusively exploitable in production.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-366)
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

    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-744)
```text
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

    /**
     * @notice Withdraws the escrowed tokens for a request body.
     * @dev This function is marked as internal.
     * @param body The request body containing commitment, tokens, and beneficiary.
     * @param isRefund Whether this is a refund (true) or a successful fill (false).
     */
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

    /**
     * @notice Handles the response for a previously dispatched storage query (GET request).
     * @dev This function is called by the host to process the response of a GET request.
     * @param incoming The response data structure for the GET request.
     * Only the host can call this function.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
}
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md (L1-9)
```markdown
# 2026-09-03 — `HostManager` deliveries are gated too, and that does not touch permissionless relaying

Chosen: `HostManager.onAccept` refuses any relayer but the one the host admin set, zero included.

The app gates check an address the host reports, and the host takes it from its handler. The
handler is a host parameter that a `SetHostParam` governance message can replace, and until now
any relayer could deliver that message once its consensus proof verified. Under a forged consensus
an attacker would swap in a handler that reports the whitelisted relayer on every message, and the
app gates would pass. Gating the HostManager closes that route.
```
