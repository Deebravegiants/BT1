## Analysis

The ThunderNFT report describes a bug class where a governance-controlled whitelist mapping check, added as a required condition inside a fund-release path, is later mutated by a legitimate protocol action — permanently bricking the release of already-escrowed assets for orders that were placed before the mutation, with no alternate recovery route.

The equivalent path in Hyperbridge is the Intent Gateway's cross-chain settlement authentication. `IntentsBase._instances` is a governance-writable mapping (updated via the `NewDeployment` request kind, processed in `_addDeployment`) that records the trusted gateway address for each remote state machine. Both `RedeemEscrow` (release input tokens to the solver after a cross-chain fill) and `RefundEscrow` (return escrow to the user after a destination-side cancel) are authenticated against this **current** mapping value, not against the value that was in force when the settlement message was originally dispatched. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

If governance re-registers/migrates the gateway address for a destination chain (e.g., to fix a bug, add a corrected deployment, or rotate a compromised instance) while a `RedeemEscrow`/`RefundEscrow` message dispatched from the *old* instance address is still in flight (awaiting relay/finalization through Hyperbridge), the message's `request.from` will no longer equal `_instance(request.source)` once it's delivered, and `_authenticate` reverts with `Unauthorized()` permanently — there is no fallback path to reprocess that specific in-flight settlement once the mapping has moved on.

### Title
Governance instance-address rotation in `_instances` permanently bricks in-flight `RedeemEscrow`/`RefundEscrow` settlement, freezing escrowed order funds - (File: evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`ExtrinsicIntents._authenticate` (and the same pattern in `evm/tron/contracts/apps/IntentGatewayV2.sol::authenticate`) validates incoming `RedeemEscrow`/`RefundEscrow` post requests by comparing `request.from` against the **live** value of `_instances[keccak256(request.source)]`, which governance can overwrite at any time via a `NewDeployment` message processed in `_addDeployment`. This binds settlement validity to a mutable, governance-controlled mapping rather than to the state that existed when the corresponding order was filled/cancelled and the settlement message was dispatched.

### Finding Description
When a solver fills a cross-chain order on the destination chain, `_fillCrossChain` dispatches a `RedeemEscrow` `PostRequest` back to the source chain with `from` set to the destination gateway's own address at dispatch time. Similarly, `_cancelFromDest` dispatches a `RefundEscrow` message. Both are pending until a relayer delivers them and the source chain's `onAccept` processes them via `_authenticate`: [2](#0-1) 

`_authenticate` recomputes the expected sender by calling `_instance(request.source)`, which reads the *current* `_instances` mapping — not a value pinned at the time the order was placed or the message was dispatched: [5](#0-4) [6](#0-5) 

`_instances` is writable at any time by governance through a `NewDeployment` message, unconditionally overwriting the prior entry with no regard for outstanding in-flight settlement messages that were dispatched under the old mapping value: [3](#0-2) 

Consequently, if a `RedeemEscrow`/`RefundEscrow` message is dispatched from the currently-registered destination gateway address, and before the relayer delivers/finalizes it through Hyperbridge governance re-registers a different address for that same state machine (e.g., a legitimate migration or bug-fix redeployment, analogous to the strategy "de-listing" in the original report), the message's `from` field permanently mismatches the now-current `_instance()` value. `onAccept` reverts with `Unauthorized()` every time it is retried, and there is no alternative code path to release the escrowed tokens tied to that specific commitment — `_orders[commitment][token]` remains locked in the source contract indefinitely.

### Impact Explanation
This is a High severity finding under the theft/freezing rubric: escrowed input tokens for an order that a solver has already fulfilled (delivering output tokens to the user on the destination chain) become permanently unrecoverable once the destination gateway instance is rotated mid-flight, since the sole remaining settlement path (`RedeemEscrow`) is bricked by the authentication mismatch. Unlike a same-chain cancel, there is no fallback re-authentication or admin override function to manually complete a stuck settlement, matching the "temporary/permanent freezing of funds" impact class from the original report, but here it directly harms a solver who already performed the honest side of the trade.

### Likelihood Explanation
This requires only an ordinary, non-malicious governance action — updating `_instances` for a state machine via `NewDeployment` (e.g., redeploying/migrating a gateway, or correcting a misconfigured address) — occurring while any `RedeemEscrow`/`RefundEscrow` message dispatched under the prior mapping is still awaiting relayer delivery/finalization through the standard Hyperbridge challenge-period pipeline. Given that finalization latency (consensus + challenge period) can span from minutes to hours, any instance rotation during that window on a chain with active in-flight orders would trigger the bug, making it a realistic and plausible occurrence rather than a purely theoretical edge case.

### Recommendation
Do not authenticate in-flight settlement messages against the *current* `_instances` mapping. Instead, either (a) pin the expected sender per order at fill/cancel time (e.g., store the destination gateway address used to dispatch the message alongside `_filled`/order state and check against that snapshot), or (b) maintain a historical/versioned registry of valid past instance addresses per chain (rather than a single overwritable slot) so that messages dispatched under a previously-valid instance remain authenticatable until they are delivered or explicitly retired, with a governance-gated escape hatch to manually settle orders whose originating instance has been deprecated.

### Proof of Concept
1. User places a cross-chain order on chain A with destination chain B; solver fills it on chain B via `fillOrder`, delivering output tokens to the user and triggering `_fillCrossChain`, which dispatches a `RedeemEscrow` `PostRequest` back to chain A with `from = <gateway B address at dispatch time>`.
2. Before this message is relayed and finalized on chain A, Hyperbridge governance dispatches a `NewDeployment` message for chain B's state machine ID pointing to a new gateway address (e.g., as part of an upgrade/migration), which `_addDeployment` applies immediately, overwriting `_instances[keccak256("B")]`.
3. The relayer subsequently submits the original `RedeemEscrow` message to chain A's `onAccept`. `_authenticate` computes `_instance(request.source)` = the new address, which no longer matches `request.from` (the old address baked into the already-dispatched message), so the call reverts with `Unauthorized()`.
4. Every retry of the same message fails identically since `_instances` has moved on and there is no mechanism to recompute or override authentication for this specific commitment — the solver's escrowed input tokens on chain A (`_orders[commitment][token]`) remain locked permanently, even though the solver already fulfilled the order on chain B.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L56-67)
```text
    /**
     * @dev Authenticates an incoming cross-chain post request by verifying that the
     * sender module matches the registered gateway instance for the source chain.
     * Reverts with InvalidInput if the sender address is malformed, or Unauthorized
     * if the sender is not the expected gateway.
     * @param request The incoming post request to authenticate.
     */
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L395-405)
```text
    /**
     * @dev Resolves the IntentGateway instance address for a given state machine.
     * Reverts with `UnknownInstance` if no remote deployment has been registered for that chain.
     * @param stateMachineId The raw state machine identifier bytes.
     * @return The gateway address for the given state machine.
     */
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L574-584)
```text
    /**
     * @dev Registers a new IntentGateway deployment for a remote state machine.
     * Called when Hyperbridge governance adds support for a new chain. The gateway
     * address is stored in `_instances` keyed by the hash of the state machine ID.
     *
     * @param body The deployment info containing the state machine ID and gateway address.
     */
    function _addDeployment(Deployment memory body) internal {
        _instances[keccak256(body.chain)] = body.gateway;
        emit DeploymentAdded({chain: string(body.chain), gateway: body.gateway});
    }
```
