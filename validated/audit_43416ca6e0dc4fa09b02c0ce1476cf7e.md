Confirmed: `_authenticate` in `ExtrinsicIntents.sol` L63-67 validates the incoming `RedeemEscrow`/`RefundEscrow` message solely against the *current* value of `_instances[keccak256(source)]`, which is mutable via `NewDeployment` (`_addDeployment`, `IntentsBase.sol` L581-584). This is a strong candidate for a "stuck funds" analog: if Hyperbridge governance rotates a chain's registered gateway address (a legitimate re-deployment/migration) after an order was already filled cross-chain but before its `RedeemEscrow` settlement message is delivered/finalized, the in-flight message — dispatched `to: abi.encodePacked(_instance(order.source))` from the *old* deployment (`ExtrinsicIntents.sol` L128-136) — will authenticate against a stale/foreign address once it reaches the source-chain gateway, since `_authenticate` compares against the now-updated `_instances` mapping, not the mapping value at fill time.Confirmed: `_post` in `ExtrinsicIntents.sol` (`RedeemEscrow`/`RefundEscrow` dispatches) always sets `timeout: 0`, i.e. these settlement messages **never time out** — there is no timeout-triggered recovery path if delivery is permanently rejected.

### Title
Rotating an IntentGateway deployment address via `NewDeployment` permanently strands in-flight `RedeemEscrow`/`RefundEscrow` settlement funds - (File: evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`IntentGatewayV2`/`ExtrinsicIntents` authenticates incoming `RedeemEscrow` and `RefundEscrow` settlement messages against the *current* value of `_instances[keccak256(sourceChain)]` rather than the value that was in effect when the corresponding order was filled/cancelled. Since Hyperbridge governance can update this mapping at any time via a `NewDeployment` message, and the settlement dispatch itself is created with `timeout: 0` (never expires), a legitimate gateway re-deployment/migration that occurs while an order is filled but its settlement message is still in flight permanently strands the escrowed input tokens with no way to authenticate delivery and no timeout-based refund path — directly analogous to the EigenLayer report's pattern where an external whitelist/registry mutation (there: strategy de-whitelisting; here: gateway address rotation) breaks a previously-valid, already-escrowed operation with no recovery mechanism.

### Finding Description
- `_addDeployment` unconditionally overwrites `_instances[keccak256(chain)]` whenever a `NewDeployment` message arrives from Hyperbridge governance: [1](#0-0) 
- `_instance()` (used both to build outgoing dispatch targets and to authenticate incoming messages) always reads this same live mapping: [2](#0-1) 
- When a solver fills a cross-chain order on the destination chain, `_fillCrossChain` immediately marks `_filled[commitment] = msg.sender` and dispatches a `RedeemEscrow` post request back to the source chain, addressed via `_instance(order.source)` *at fill time*: [3](#0-2) [4](#0-3) 
- On arrival at the source chain, `onAccept` calls `_authenticate`, which compares the message's `from` field against `_instance(request.source)` **read at delivery time**, not at dispatch time: [5](#0-4) [6](#0-5) 
- The `_post` helper dispatches these settlement messages with `timeout: 0`, meaning they never expire and can never trigger `onPostRequestTimeout`-style recovery: [4](#0-3) 
- `RefundEscrow` (dispatched from `_cancelFromDest`, which also marks `_filled[commitment]` immediately before posting) has the identical exposure: [7](#0-6) 

If Hyperbridge governance legitimately re-deploys/rotates the destination-chain (or source-chain) gateway — dispatching a new `NewDeployment` to update `_instances` — while a `RedeemEscrow` or `RefundEscrow` message from the *old* deployment is still traversing the challenge period / relayer pipeline, the message's `from` address will no longer match `_instance(request.source)` by the time it is delivered. `onAccept` reverts with `Unauthorized()` for every delivery attempt (a relayer can keep retrying, but the check is deterministic and will never pass since the old address is permanently gone from the mapping). Because the dispatch used `timeout: 0`, there is no timeout path on the source chain to fall back to and refund the user/solver. The escrowed input tokens (`_orders[commitment][token]`) remain locked in `_orders` forever, and:
- For `RedeemEscrow`: the solver already delivered the full output amount to the beneficiary on the destination chain but can never collect the escrowed input tokens.
- For `RefundEscrow`: the user's order was already marked filled/cancelled on the destination chain (blocking any future fill) but the source-chain escrow refund can never land.

This mirrors the EigenLayer report's root cause exactly: a mutable external registry entry (strategy whitelist / gateway instance mapping) that funds already committed to a specific route depend on, with no mechanism to update the stale reference or fall back to a refund once it changes.

### Impact Explanation
Escrowed order inputs become permanently unrecoverable (frozen indefinitely, with no admin/user function that can force-release them since `_withdraw` is only reachable through the two message-authenticated code paths above and `cancelOrder`'s `Filled()` guard rejects any competing withdrawal attempt once `_filled` is already set). This is a direct, permanent freezing-of-funds impact affecting real user/solver capital moved through IntentGateway cross-chain fills and cancellations, warranting High severity.

### Likelihood Explanation
Gateway re-deployments/migrations are an expected part of protocol operations (the codebase explicitly supports `NewDeployment` for exactly this purpose, and there's an `Execute`/`upgradeToAndCall` path for upgrades too). Any order that is filled or destination-cancelled in the narrow window before a `NewDeployment` update propagates and finalizes — i.e., whenever governance rotates a chain's registered instance while cross-chain settlement traffic is in flight — triggers this permanently-stuck state. No malicious actor is required; a routine, honest governance action combined with normal operational timing is sufficient, making likelihood plausible under normal operation.

### Recommendation
Snapshot the expected counterparty address into the dispatched message context (or into per-order state) at fill/cancel time rather than re-deriving it from the live `_instances` mapping on delivery, so a later `NewDeployment` rotation cannot invalidate messages already in flight. Alternatively/additionally: (1) give `RedeemEscrow`/`RefundEscrow` dispatches a non-zero `timeout` and implement `onPostRequestTimeout` to refund the escrow if the settlement message cannot be authenticated/delivered before expiry, and (2) when rotating `_instances` via `NewDeployment`, retain the old address as a still-valid sender for some grace/drain period (or require handling in-flight settlement before allowing the swap) so previously dispatched, honestly-filled orders can always settle.

### Proof of Concept
1. Solver calls `fillOrder` on the destination chain for a cross-chain `Order`; `_fillCrossChain` sets `_filled[commitment] = solver` and dispatches `RedeemEscrow` to `_instance(order.source)` = `GatewayA` (the source chain's currently-registered instance) — [3](#0-2) .
2. Before the `RedeemEscrow` message is relayed/finalized through Hyperbridge, governance dispatches `NewDeployment{chain: destChain, gateway: GatewayB}` to the source chain, which `_addDeployment` applies, overwriting `_instances[keccak256(destChain)]` from `GatewayA` to `GatewayB` — [1](#0-0) .
3. A relayer submits the `RedeemEscrow` proof to the source-chain host; `onAccept` calls `_authenticate`, which now compares `request.from` (`GatewayA`) against `_instance(request.source)` which resolves to `GatewayB` — mismatch, reverts `Unauthorized()` — [5](#0-4) .
4. Because the dispatch used `timeout: 0`, the message never times out, so no `onPostRequestTimeout`/refund path exists — [4](#0-3) .
5. `_orders[commitment][token]` remains permanently escrowed; the solver, having already paid out the full output amount on the destination chain, can never redeem the input tokens, and no other function can force-release them since `_filled[commitment]` is already non-zero on the destination side and `cancelOrder`'s checks are keyed off the same stale routing assumption.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L581-584)
```text
    function _addDeployment(Deployment memory body) internal {
        _instances[keccak256(body.chain)] = body.gateway;
        emit DeploymentAdded({chain: string(body.chain), gateway: body.gateway});
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L63-67)
```text
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L128-142)
```text
    function _post(Order calldata order, bytes memory body, uint256 relayerFee, uint256 nativeFee) internal {
        DispatchPost memory request = DispatchPost({
            dest: order.source,
            to: abi.encodePacked(_instance(order.source)),
            body: body,
            timeout: 0,
            fee: relayerFee,
            payer: msg.sender
        });
        if (nativeFee > 0) {
            IDispatcher(host()).dispatch{value: nativeFee}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-219)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-307)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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
