Based on my research, I found a direct analog in `evm/src/apps/IntentGatewayV2.sol`'s `placeOrder` function.

### Title
`placeOrder` escrows user funds against an unvalidated, possibly unregistered `order.destination` - (File: `evm/src/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder()` accepts a caller-supplied `order.destination` and immediately escrows the user's input tokens under a commitment keyed to that destination, without ever checking that a gateway `instance` is registered for it.

### Finding Description
`placeOrder` in `evm/src/apps/IntentGatewayV2.sol` never calls `instance()`/`_instance()` to validate `order.destination` before escrowing funds. The function only checks `order.inputs.length == 0` and duplicate tokens, then proceeds straight to token transfer, fee computation keyed by `keccak256(order.destination)`, and escrow accounting in `_orders[commitment][token]`. [1](#0-0) [2](#0-1) 

Compare this to `_instance()`, which is the canonical validator for a state machine id and reverts with `UnknownInstance` when no deployment is registered — but `placeOrder` never calls it: [3](#0-2) 

The only place that actually enforces a registered instance is `authenticate()`, used for *incoming* cross-chain messages (e.g. `RedeemEscrow`/`RefundEscrow`), which requires the message to originate from a known instance address: [4](#0-3) 

Instances are only added through governance via `NewDeployment`/`_addDeployment`, keyed by `keccak256(chain)`: [5](#0-4) 

If a user (or a UI/SDK bug, analogous to Bob's mistaken `_vaultNumber` in the original report) supplies a `destination` string that has no corresponding registered `_instances` entry, `placeOrder` happily escrows the funds and emits `OrderPlaced` with that destination. This mirrors the reported bug class exactly: an unvalidated identifier is accepted and persisted (here, the escrow commitment tied to a destination chain) before any downstream mechanism that depends on that identifier being valid.

### Impact Explanation
No solver on any real chain can ever match/fill this order for a destination gateway that doesn't exist, since no legitimate gateway instance is deployed there to emit the fill and no relayed `RedeemEscrow` message can be authenticated back to the correct destination-side gateway address (`authenticate` requires `instance(request.source) == module`, which itself depends on the same registration). The user's escrowed input tokens become effectively stuck, only recoverable (if at all) through whatever timeout/cancellation path is gated by the destination gateway's confirmation, which likewise cannot be produced for an unregistered destination. This is a direct parallel to the reported "users could lose their rewards" issue: escrowed funds tied to an unvalidated destination identifier become unreachable, resulting in loss of user funds.

### Likelihood Explanation
Likelihood is moderate: it requires either a user/integrator mistake (wrong chain string) or a solver/UI bug that passes an unsupported or mistyped `destination`. Since `placeOrder` is a fully permissionless, unprivileged entry point reachable by any user with a single transaction, and there is zero validation of the destination against `_instances`, the bug is trivially reachable without any privileged role.

### Recommendation
Add a check in `placeOrder` (mirroring `_instance()`'s revert-on-unknown behavior) that `order.destination` resolves to a registered `_instances[keccak256(order.destination)]` before any tokens are transferred or escrow state written, e.g. call `_instance(order.destination)` early in `placeOrder` and revert with `UnknownInstance` if unregistered.

### Proof of Concept
1. Deploy `IntentGatewayV2` and initialize normally; do not register a deployment for state machine id `"UNKNOWN_CHAIN"`.
2. A user calls `placeOrder(order, graffiti)` with `order.destination = bytes("UNKNOWN_CHAIN")` and valid `order.inputs`.
3. `placeOrder` succeeds: tokens are transferred from the user, `_orders[commitment][token]` is set, and `OrderPlaced` is emitted — despite `intentGateway.instance(bytes("UNKNOWN_CHAIN"))` reverting with `UnknownInstance` per the existing test `testInstance`. [6](#0-5) 
4. No gateway exists at `"UNKNOWN_CHAIN"` to produce a valid fill or a `RedeemEscrow`/`RefundEscrow` message that `authenticate()` would accept, since `authenticate` requires the message to come from the registered instance for that source — which was never set. The user's escrowed funds are left with no valid path to release.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-196)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

```

**File:** evm/src/apps/IntentGatewayV2.sol (L331-368)
```text
        // Phase 2: Compute protocol fees and commitment from actual received amounts.
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                if (originalAmount == 0) revert InvalidInput();
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            order.inputs = reducedInputs;
        } else {
            reducedInputs = order.inputs;
        }
        commitment = keccak256(abi.encode(order));

        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3149-3155)
```text
    function testInstance() public {
        bytes memory stateMachineId = bytes("TEST_CHAIN");

        // An unregistered chain reverts with UnknownInstance.
        vm.expectRevert(IntentsBase.UnknownInstance.selector);
        intentGateway.instance(stateMachineId);

```
