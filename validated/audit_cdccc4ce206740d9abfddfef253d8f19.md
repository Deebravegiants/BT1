Confirmed: only `ExtrinsicIntents.sol` (the standard EVM IntentGateway) implements `onAccept` and `IntentGatewayV2.sol` (Tron) is the only other implementation with the `RequestKind`-dispatching `onAccept`. There is no separate non-Tron `IntentGatewayV2.sol`; `ExtrinsicIntents` is the canonical implementation. Comparing the two `onAccept` bodies shows the Tron variant is missing the `RequestKind.Execute` branch that exists in `ExtrinsicIntents`.

### Title
Tron `IntentGatewayV2.onAccept` cannot handle the `Execute` `RequestKind`, blocking governance's only door to host-restricted functions - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentsBase.RequestKind` defines six discriminators, including `Execute` (value 5), documented as "Governance's one door to the host-only functions: `upgradeToAndCall` for upgrades, `setRelayer` for rotations." [1](#0-0)  `ExtrinsicIntents.onAccept`, the standard EVM IntentGateway's incoming-message handler, decodes this discriminator and reaches it via `Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:])`, explicitly preserving `msg.sender` as the host so host-only functions like `upgradeToAndCall` and `setRelayer` remain reachable. [2](#0-1)  The Tron `IntentGatewayV2.onAccept`, which shares the identical `RequestKind` enum and the same request-decoding pattern, handles `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, and `SweepDust` but has no `else if (kind == RequestKind.Execute)` branch at all. [3](#0-2) 

### Finding Description
Both `ExtrinsicIntents` and the Tron `IntentGatewayV2` extend `IntentsBase` and share its `RequestKind` enum, which is the wire discriminator for the first byte of any Hyperbridge-delivered POST body. [4](#0-3)  `onAccept` in both contracts is `onlyHost`, decodes `RequestKind(uint8(incoming.request.body[0]))`, and then authenticates or authorizes based on the kind. [5](#0-4) 

`ExtrinsicIntents.onAccept` falls through to a final `else if (kind == RequestKind.Execute)` that delegatecalls the current implementation, which is the only route by which host-only functions such as `setRelayer` and `upgradeToAndCall` can be invoked (since they check `msg.sender == host()` and the delegatecall preserves that from the host's original `dispatchIncoming` call). [6](#0-5)  The Tron `onAccept` ends its `if/else if` chain after `SweepDust` with no equivalent branch, silently returning without executing anything when `kind == RequestKind.Execute` is dispatched, since the body byte `5` matches none of the checked cases. [7](#0-6) 

This mirrors the referenced report's bug class exactly: a base/sibling implementation adds handling for a new dispatch discriminator, but a parallel chain-specific override/variant is not updated to match, leaving that code path silently unreachable on one chain.

### Impact Explanation
Because `Execute` is documented as governance's "one door" to host-restricted functions (`upgradeToAndCall`, `setRelayer`) on the gateway, the Tron deployment of `IntentGatewayV2` can never receive an `Execute` dispatch from Hyperbridge. Any governance action relying on this path — rotating the authorized relayer (`setRelayer`) or upgrading the proxy implementation (`upgradeToAndCall`) — is unreachable on Tron. This is a Medium-severity route-availability/liveness issue: it does not itself leak or freeze escrowed funds directly, but it permanently blocks Hyperbridge governance's only mechanism to rotate the relayer or upgrade a compromised/buggy Tron gateway, which can become critical if the deployed relayer key is later compromised or a bug requiring an upgrade is found, since there is no way to react.

### Likelihood Explanation
This will trigger deterministically and unconditionally the first time Hyperbridge dispatches an `Execute`-kind request (discriminator `5`) to the Tron `IntentGatewayV2` instance — no adversarial conditions are needed, it is a straightforward code-path gap reachable by any legitimate governance dispatch from Hyperbridge (source-authenticated via `keccak256(incoming.request.source) == hyperbridge()`). [8](#0-7) 

### Recommendation
Add the missing `else if (kind == RequestKind.Execute) { Address.functionDelegateCall(...) }` branch to `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `onAccept`, mirroring `ExtrinsicIntents.onAccept` exactly (including the same access-control gating that restricts it to Hyperbridge-only dispatch), and add a regression test asserting `Execute` dispatch reaches `setRelayer`/`upgradeToAndCall` on the Tron contract identically to the EVM `ExtrinsicIntents` contract.

### Proof of Concept
1. Hyperbridge governance dispatches a POST request to the Tron `IntentGatewayV2` instance with `body[0] = 5` (i.e., `RequestKind.Execute`) and `body[1:]` encoding a call to `setRelayer(newRelayer)`.
2. `EvmHost.dispatchIncoming` (or Tron's equivalent) calls `IntentGatewayV2.onAccept`, which passes the `onlyHost` check. [9](#0-8) 
3. `kind` is `RequestKind.Execute` (value `5`), which does not match `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, or `SweepDust`. [10](#0-9) 
4. The function falls through and returns without reverting and without performing the delegatecall, so `setRelayer` is never invoked — the relayer rotation silently fails with no error surfaced to governance, compare to `ExtrinsicIntents.onAccept`'s explicit `Execute` handling at lines 347-348. [11](#0-10)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L88-120)
```text
     * @dev Discriminator for cross-chain request types dispatched via Hyperbridge.
     * Encoded as the first byte of the request body in onAccept.
     */
    enum RequestKind {
        /**
         * @dev Release escrowed tokens to the solver after a successful cross-chain fill.
         */
        RedeemEscrow,
        /**
         * @dev Register a new gateway deployment for a remote state machine.
         */
        NewDeployment,
        /**
         * @dev Update gateway configuration parameters and destination fees.
         */
        UpdateParams,
        /**
         * @dev Sweep accumulated protocol dust to a beneficiary.
         */
        SweepDust,
        /**
         * @dev Refund escrowed tokens to the user after a cross-chain cancellation.
         */
        RefundEscrow,
        /**
         * @dev Delegatecall the current implementation with the rest of the body as calldata, the
         * host still `msg.sender`. Governance's one door to the host-only functions:
         * `upgradeToAndCall` for upgrades, `setRelayer` for rotations. Same discriminator as the
         * `UpgradeContract` action of earlier implementations, whose `(address, bytes)` body
         * selects no function here and reverts.
         */
        Execute
    }
```

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
