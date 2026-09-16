Based on the evidence gathered, there is a valid analog in this codebase.

### Title
Missing relayer-allowlist gate in the Tron IntentGatewayV2's `onAccept`/`onGetResponse` allows forged escrow redemption/refund and governance actions - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Poweradmin bug is a class of "duplicate authorization logic, one path missing a check": the web controller enforces a superuser-edit guard and a password-permission guard that the parallel REST API path omits, letting a low-privileged caller take an action (reset the admin password) that the equivalent, better-guarded code path forbids. The same pattern exists between the EVM IntentGatewayV2 and its Tron counterpart in this repository.

### Finding Description
On 2026-09-03 a relayer-allowlist gate was added to the canonical `IntentGatewayV2`/`ExtrinsicIntents` contract: `onAccept` and `onGetResponse` now call `_checkRelayer(incoming.relayer)` *before* the request body is decoded, so escrow redemptions, refunds, and every governance action (including upgrades) are gated to a single authorised relayer address. [1](#0-0) [2](#0-1) 

The Tron variant of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements the identical dispatch surface (`onAccept` handling `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`, and `onGetResponse`), but its `onAccept` and `onGetResponse` never call any relayer-allowlist check — there is no `_checkRelayer`, no `_relayer` state, and no `setRelayer` in this file at all (confirmed by a repo-wide grep restricted to `evm/tron/**` returning zero matches for `_relayer`, `checkRelayer`, or `setRelayer`, and only self-referential matches inside `IntentGatewayV2.sol` itself for unrelated identifiers). The only gates present are `onlyHost` (checks the call came from the local host contract) and `authenticate`/an `IDispatcher(host()).hyperbridge()` source check for governance actions — both check *where the message came from*, not *who relayed it*. [3](#0-2) 

This mirrors the Poweradmin defect exactly: `ApiPermissionService::canEditUser` (API) lacks the superuser check that `EditUserController` (web) enforces; here, the Tron `onAccept`/`onGetResponse` lack the `_checkRelayer` gate that the canonical EVM `ExtrinsicIntents::onAccept`/`onGetResponse` enforce, even though both are meant to be the same trust boundary for the same protocol action.

### Impact Explanation
On Tron deployments of `IntentGatewayV2`, any relayer capable of delivering a valid ISMP message through the local host (i.e., any party running a copy of the standard relayer flow, not a specially-privileged one) can trigger `RedeemEscrow`/`RefundEscrow` withdrawals and governance-adjacent state changes (`NewDeployment`, `UpdateParams`, `SweepDust`) without being the single relayer the protocol intends to trust for this gateway. Where the EVM version treats an unlisted relayer's delivery as unauthorized and retryable only by the allow-listed relayer, the Tron version accepts it from anyone whose delivery reaches `onAccept`/`onGetResponse` via the host — this is a direct path to unauthorized withdrawal of escrowed intent funds and unauthorized configuration changes (`UpdateParams` changes protocol fees; `SweepDust` moves accumulated dust to an attacker-chosen beneficiary if the source check on those particular actions can be satisfied/spoofed by an unlisted relayer delivering a genuine Hyperbridge-sourced message).

### Likelihood Explanation
Likelihood is high wherever this Tron contract is actually deployed and live: exploitation requires no more than being a relaying party able to get a validly-sourced ISMP post request delivered through the host to this app — the exact same "unprivileged relayer" actor class explicitly in scope for this analysis. No admin key, governance vote, or protocol-level compromise is needed; the missing check is purely a code-path omission analogous to the Poweradmin API gap.

### Recommendation
Port the `_relayer`/`_checkRelayer`/`setRelayer` allowlist mechanism from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` (and its `IntentsBase`) into `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling `_checkRelayer(incoming.relayer)` at the very top of both `onAccept` and `onGetResponse`, before the request body is decoded — mirroring the fix already applied to the canonical EVM contract.

### Proof of Concept
1. Deploy/observe a live Tron `IntentGatewayV2` instance with escrowed orders (via `placeOrder`).
2. An arbitrary relayer (not the intended, singular trusted relayer used on the EVM side) constructs and delivers a valid Hyperbridge-sourced `PostRequest` with body `RequestKind.RedeemEscrow` (or `RefundEscrow`) for an existing commitment, through the local host's normal delivery path so that `onlyHost` is satisfied.
3. `onAccept` runs `authenticate(incoming.request)` (checks only the request's *source module*, not the relayer) and proceeds to `withdraw(...)`, releasing escrowed tokens to the attacker-controlled beneficiary encoded in the request — with no check on `incoming.relayer` at all.
4. Compare against the equivalent call on the canonical EVM contract, where `testOnAcceptRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol` shows the identical delivery reverting with `Unauthorized()` when the relayer is not the allow-listed one. [4](#0-3) 

**Note on confidence**: I was unable to execute a terminal/filesystem check (e.g., deployment scripts, migrations, or `tronbox.js` config) to confirm this Tron contract is actively deployed to production Tron rather than being a stale/legacy copy pending the same relayer-allowlist backport, since read_file calls failed to return content for `evm/tron/README.md` and `evm/tron/tronbox.js` in this session. If a Devin session with full file/filesystem access confirms this contract is not live in production (e.g., marked deprecated, unreferenced by deploy scripts, or superseded), this finding's severity should be downgraded accordingly.

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

**File:** sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md (L1-14)
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

The interface gains `RelayerUpdated(address previous, address current)` and `setRelayer`, keeping
its declarations identical to `IntentsBase`. The unused `_paused` getter was dropped from the gateway
to stay under the EIP-170 size limit; it was never declared here.
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
