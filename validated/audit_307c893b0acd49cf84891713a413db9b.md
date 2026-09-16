### Title
`NewDeployment` Instance Reassignment In IntentGatewayV2 Orphans In-Flight Cross-Chain Fills And Escrowed Orders - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`IntentGatewayV2` resolves the trusted counterparty gateway for every remote chain through a single overwritable mapping, `_instances`. A `NewDeployment` governance message unconditionally replaces the registered address for a state machine with no regard for orders already escrowed against, or already filled by, the previous instance. Any `RedeemEscrow`/`RefundEscrow` message still in flight from the old instance is permanently rejected once the pointer moves, and the destination-chain proof read used for cancellation is silently redirected to the new (empty) instance — this is the same bug class as the SecondSwap `VestingManager.setMarketplace` finding: an atomic pointer swap to a "new" counterparty leaves state tied to the "old" counterparty permanently unreachable.

### Finding Description
`_instances` is written only by `_addDeployment`, which overwrites the previous entry with no history and no draining/migration step: [1](#0-0) 

`_instance` is the sole reader used both to authenticate inbound settlement messages and to address outbound ones: [2](#0-1) 

On the settlement path, `_authenticate` requires the sender of a `RedeemEscrow`/`RefundEscrow` message to equal the *current* `_instance(request.source)`: [3](#0-2) [4](#0-3) 

`NewDeployment` is processed in the very same `onAccept`, gated only by "message sourced from Hyperbridge," with no check for whether the state machine already has escrowed/in-flight orders against the address being replaced: [5](#0-4) 

Concretely:
1. A user places a cross-chain order on chain A, escrowing input tokens in `_orders[commitment][token]` (source escrow, independent of any registry).
2. A solver fills the order on chain B's currently-registered gateway (`gatewayB_old`); `_fillCrossChain` sets `_filled[commitment] = solver` and dispatches a `RedeemEscrow` post request to chain A, addressed via `_instance(order.source)` as seen from `gatewayB_old`: [6](#0-5) 
3. Before that message is relayed and delivered, Hyperbridge governance issues a legitimate `NewDeployment` for chain B (e.g. a full redeploy of the gateway rather than a proxy upgrade — exactly the scenario the SecondSwap report describes for `setMarketplace`). Chain A's `_instances[keccak256(chainB)]` now points to `gatewayB_new`.
4. When the `RedeemEscrow` message from `gatewayB_old` is finally relayed to chain A, `_authenticate` computes `module = gatewayB_old` and compares it against `_instance(chainB) = gatewayB_new` — the check fails with `Unauthorized`, and the message can never succeed no matter how many times it is retried, since the registry entry cannot be reverted to the value needed for this specific message.
5. The input tokens remain locked in chain A's `_orders` mapping forever: the solver already delivered the promised outputs on chain B but can never redeem the escrow (`_orders[commitment][token]` is never decremented, `_withdraw` is never reached).
6. Symmetrically, `_cancelFromSource` builds its storage-proof key from the *current* `_instance(order.destination)` (now `gatewayB_new`) rather than the address the order actually filled against: [7](#0-6)  — the proof reads an empty `_filled` slot on the new, unrelated contract, so `onGetResponse` incorrectly concludes the order was never filled and refunds the user's escrow: [8](#0-7) . This produces a double-payment: the solver already paid the beneficiary on chain B, then the user is *also* refunded on chain A, at the solver's total loss.

### Impact Explanation
Both branches result in concrete loss of user/solver funds without any recovery path once the registry is repointed: escrow permanently stuck (case 4-5) or solver double-paid via a spurious refund (case 6). This matches "permanent freezing of funds" / "unbacked release," meeting High severity, since it is reachable by any solver/user simply racing an ordinary cross-chain fill or cancellation against a legitimate `NewDeployment` governance update — no malicious governance action is required, only a normal redeploy of a peer gateway while orders are in flight, which is exactly the acknowledged root cause in the SecondSwap report.

### Likelihood Explanation
`NewDeployment` is an expected, documented governance action for adding/rotating chain support, and cross-chain fills/cancellations routinely take multiple blocks (source dispatch → Hyperbridge finalization → relayer delivery) during which a redeploy could plausibly occur. Given IntentGatewayV2 is upgradeable via `Execute`/`upgradeToAndCall` for normal upgrades, a `NewDeployment` would realistically only be used for a genuine address change (a full redeploy, e.g. after key compromise or infra migration) — precisely the scenario most likely to have in-flight orders. Likelihood is Medium.

### Recommendation
- Do not fully overwrite `_instances` entries; instead, retain the ability to authenticate and settle messages against any address that was ever registered for that state machine (e.g., keep a set/history of valid instances per chain rather than a single mapping slot), or
- Require a drain/migration window: before a `NewDeployment` for a chain with a currently non-zero instance is accepted, require that chain's in-flight commitments be settled, or provide an explicit escape hatch letting affected order owners withdraw escrow tied to a superseded instance rather than relying on the (now broken) cross-chain authentication/cancellation path.

### Proof of Concept
1. Deploy `IntentGatewayV2` on chain A and chain B (`gatewayB_old`), register each as the other's peer via `initialize`.
2. User places a cross-chain order on chain A with `destination = chain B`, escrowing `usdc` (see `testOnAcceptRefundEscrow` for the escrow bookkeeping pattern): [9](#0-8) 
3. Solver fills the order on `gatewayB_old`, which internally calls `_fillCrossChain`, dispatching a `RedeemEscrow` request destined for chain A.
4. Before that request is delivered, dispatch a `NewDeployment` message to chain A's gateway pointing chain B's slot at `gatewayB_new` (see the registration flow exercised in `testInstance`): [10](#0-9) 
5. Deliver the pending `RedeemEscrow` request to chain A's gateway via `onAccept` — `_authenticate` reverts with `Unauthorized` because `request.from` (`gatewayB_old`) no longer equals `_instance(chainB)` (`gatewayB_new`). The escrow tied to that commitment can never be released; retrying the same message deterministically reverts.
6. Alternatively, have the user call `cancelOrder`/`_cancelFromSource` after the swap; the storage-proof key is built against `gatewayB_new`'s empty `_filled` slot, so `onGetResponse` refunds the user even though the order was already filled and paid out on `gatewayB_old`.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L63-67)
```text
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-212)
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
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L254-259)
```text
        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L339-342)
```text
        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            _addDeployment(abi.decode(incoming.request.body[1:], (Deployment)));
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L2293-2321)
```text
    function testOnAcceptRefundEscrow() public {
        uint256 inputAmount = 1000 * 1e6;

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(uint256(uint160(user))),
            source: host.host(),
            destination: host.host(),
            deadline: block.number + 1000,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3149-3178)
```text
    function testInstance() public {
        bytes memory stateMachineId = bytes("TEST_CHAIN");

        // An unregistered chain reverts with UnknownInstance.
        vm.expectRevert(IntentsBase.UnknownInstance.selector);
        intentGateway.instance(stateMachineId);

        // Register an explicit override deployment
        address gateway = address(0xABCD);
        Deployment memory deployment = Deployment({chain: stateMachineId, gateway: gateway});

        bytes memory body = bytes.concat(bytes1(uint8(IntentsBase.RequestKind.NewDeployment)), abi.encode(deployment));

        PostRequest memory request = PostRequest({
            source: host.hyperbridge(),
            dest: host.host(),
            nonce: 0,
            from: abi.encodePacked(address(intentGateway)),
            to: abi.encodePacked(address(intentGateway)),
            body: body,
            timeoutTimestamp: 0
        });

        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: request}));

        // Now should return the stored gateway
        address instance = intentGateway.instance(stateMachineId);
        assertEq(instance, gateway, "Should return stored gateway address");
    }
```
