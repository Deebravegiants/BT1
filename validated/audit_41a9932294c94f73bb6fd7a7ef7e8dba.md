## Title
Missing relayer allowlist gate on the Tron `IntentGatewayV2` allows unauthorised delivery of escrow redemption, refund, and governance actions — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

## Summary
The EVM `IntentGatewayV2` (`evm/src/apps/IntentGatewayV2.sol` / `evm/src/apps/intentsv2/ExtrinsicIntents.sol`) was hardened with a relayer allowlist gate (`_checkRelayer`) that restricts which relayer address may deliver `onAccept`/`onGetResponse` callbacks once armed, specifically to prevent an arbitrary relayer from delivering escrow redemptions, refunds, and governance actions (upgrades, `NewDeployment`, `UpdateParams`, `SweepDust`, `Execute`). The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements identical business logic (`onAccept`, `onGetResponse`, `withdraw`, `authenticate`) but never received this fix — it has no `_relayer`, `_checkRelayer`, or `setRelayer`, relying solely on `onlyHost`.

## Finding Description
`onlyHost` on the Tron contract only verifies that `msg.sender == host()`, i.e. that the call arrived through the real `IHost` after proof verification. It says nothing about *which relayer* submitted the proof. In the hardened EVM version, this gap was deliberately closed because of the following attack, explicitly documented as "the attack the gate exists for" in `evm/tests/foundry/HostManagerTest.sol` and related decision docs: an unauthorised relayer (or an attacker who can influence a `handler`/consensus swap or otherwise get an arbitrary account recorded as the delivering relayer) can be the one whose address is passed as `incoming.relayer` in `IncomingPostRequest`, and every downstream governance/escrow action trusts that value implicitly unless gated.

Concretely, on Tron:
```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        authenticate(incoming.request);
        WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
        return withdraw(body, kind == RequestKind.RefundEscrow);
    }
    if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
    ... // NewDeployment, UpdateParams, SweepDust
}
``` [1](#0-0) 

there is no equivalent of:
```solidity
function _checkRelayer(address relayer) internal view {
    address authorised = _relayer;
    if (authorised != address(0) && relayer != authorised) revert Unauthorized();
}
``` [2](#0-1) 

which the EVM `onAccept`/`onGetResponse` run *before* decoding the message body:
```solidity
_checkRelayer(incoming.relayer);
RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
``` [3](#0-2) 

The design rationale is captured directly in the flow documentation:
"3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts with `Unauthorized` when a relayer is set and the delivery is from anyone else... `onGetResponse` has the same two steps before touching the response." [4](#0-3) 

and the HostManager test explicitly frames this as defense against an attacker able to make the reported relayer arbitrary via a forged/replaced handler:
"The attack the gate exists for: a forged SetHostParam that swaps the host's handler for a contract that will report any relayer address. With the gate, an arbitrary relayer cannot deliver the swap..." [5](#0-4) 

Since the Tron `IntentGatewayV2` never got this gate, any account that can get itself recorded as `incoming.relayer` for a `dispatchIncoming` call on the Tron host (or that legitimately controls/compromises the relaying handler/consensus configuration on Tron) can directly deliver `RedeemEscrow`/`RefundEscrow` (draining escrowed order funds to any beneficiary once `authenticate` passes) or governance actions (`NewDeployment`, `UpdateParams`, `SweepDust`) without being the intended, singly-authorised relayer that the rest of the protocol assumes gates these actions.

## Impact Explanation
This is a broken-authorization analog to CVE-2022-1936: a credential-equivalent check (which relayer is trusted to deliver privileged cross-chain actions) that exists and is enforced on the primary EVM deployment is silently absent on the Tron deployment of the identical contract, letting the restricted action (escrow release/refund, protocol parameter changes, dust sweeping, new-deployment registration) be performed by an unintended party. On the intents/escrow path this directly threatens theft/misdirection of escrowed funds and unauthorized governance action, satisfying "unauthorized app action" / "concrete theft ... of funds" per the validation criteria. It is reachable from a single relayed/dispatched request on the Tron host — no admin/governance collusion required beyond the pre-existing trust in whichever handler records `msg.sender` as the relayer.

## Likelihood Explanation
Likelihood depends on how tightly Tron's handler/consensus-client configuration constrains who can appear as `incoming.relayer` for `dispatchIncoming`. Under the shared EVM host design (`EvmHost.dispatchIncoming` forwards `_msgSender()` from the handler as the relayer with no additional restriction), any account able to submit a valid proof to the Tron handler becomes the "relayer" for that delivery — which on Tron is completely permissionless by design (any prover with a valid proof), meaning *every* deliverer is implicitly "authorised" because there is no allowlist to bypass. This is the intended permissionless-relayer model elsewhere in the codebase, but it directly contradicts the security guarantee the EVM gateway's relayer gate is documented to provide for this exact contract (single authorised relayer for escrow/governance actions). Because Tron intentionally lacks any equivalent guard, the described bypass is not a corner-case exploit but the default, always-reachable behavior for anyone who can relay a valid cross-chain proof to the Tron gateway.

## Recommendation
Port the same `_relayer` / `_checkRelayer` / `setRelayer` mechanism (or an equivalent restriction) from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, gating `onAccept` and `onGetResponse` on the authorised relayer before decoding `RequestKind`, consistent with the EVM gateway's documented threat model. Alternatively, if Tron's design intentionally omits the gate, this must be explicitly documented as a deliberate divergence with a justified threat model, since currently it silently regresses a security control that the rest of the codebase treats as necessary for this exact contract.

## Proof of Concept
1. On the Tron `IntentGatewayV2`, a user places a cross-chain `Order` via `placeOrder`, escrowing input tokens.
2. Any account capable of relaying a valid delivery proof to the Tron `IHost` (permissionless relaying) submits the destination-side `RedeemEscrow`/`RefundEscrow` `PostRequest` such that `dispatchIncoming` calls `IntentGatewayV2.onAccept(IncomingPostRequest(request, relayer))` with `relayer` being that account's own address.
3. `onAccept` checks only `onlyHost` and, for `RedeemEscrow`/`RefundEscrow`, `authenticate(request)` (source-module check) — never checking `incoming.relayer` — then calls `withdraw`, releasing escrowed funds to the beneficiary encoded in the message body regardless of who the "authorised" relayer was supposed to be. [6](#0-5) 
4. Compare against the EVM gateway, where the identical flow first reverts with `Unauthorized` unless `incoming.relayer` matches `_relayer` (proven by `testOnAcceptRejectsUnlistedRelayer` and `testOnGetResponseRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol`), showing the Tron contract lacks a control the test suite treats as required. [7](#0-6)

### Citations

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L329-340)
```text
     */
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

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L14-17)
```markdown
3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts
   with `Unauthorized` when a relayer is set and the delivery is from anyone else. Only then is the
   first body byte read as a `RequestKind`. `onGetResponse` has the same two steps before touching
   the response.
```

**File:** evm/tests/foundry/HostManagerTest.sol (L221-225)
```text
    /// The attack the gate exists for: a forged SetHostParam that swaps the host's handler for a
    /// contract that will report any relayer address. With the gate, an arbitrary relayer cannot
    /// deliver the swap, so the handler stays honest and the attacker's contract never becomes
    /// able to call the host.
    function testForgedHandlerSwapIsRefused() public {
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
