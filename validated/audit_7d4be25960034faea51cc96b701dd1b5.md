### Title
Orders can be placed for a destination chain with no registered gateway instance, permanently freezing escrowed funds - (File: `evm/src/apps/IntentGatewayV2.sol`, `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder()` never validates that `order.destination` has a registered peer gateway (via `instance()`/`_instance()`, populated only through `_addDeployment` at `initialize` or a subsequent `NewDeployment` cross-chain message). A user can escrow tokens for any arbitrary `destination` bytes string, even one for which no counterpart `IntentGatewayV2` has been deployed/registered yet, or for which registration ("upkeep"/relayer infrastructure equivalent to the Chainlink keeper job) has not been confirmed. This mirrors the referenced Chainlink report: an action ("create order" / "register upkeep") that depends on an asynchronous, unconfirmed cross-chain registration step is allowed to proceed immediately, based only on the caller's say-so about the destination.

### Finding Description
`placeOrder` in `evm/src/apps/IntentGatewayV2.sol` (and the duplicated Tron implementation `evm/tron/contracts/apps/IntentGatewayV2.sol`) escrows `order.inputs` and emits `OrderPlaced` for whatever `order.destination` the caller supplies: [1](#0-0) 

The only place a destination is checked against the registered/instance mapping is `instance()`, which reverts with `UnknownInstance` — but this check exists as a public helper and is used by `fillOrder`/cancellation flows, not by `placeOrder`: [2](#0-1) 

Registered destinations are populated only at `initialize` (fixed set of `peerChains`) or later via a `NewDeployment` cross-chain governance message (the async, off-chain-confirmed equivalent of Chainlink's keeper registrar approval): [3](#0-2) 

Fee lookup at placement time explicitly tolerates an unregistered/unknown destination by falling back to the default protocol fee rather than rejecting the order — confirmed by the test placing an order to `"UNKNOWN_CHAIN"`: [4](#0-3) [5](#0-4) 

Because there is no check tying `order.destination` to a confirmed/registered peer gateway (`instance(order.destination)` succeeding), a user's order can be placed for a chain/gateway that:
- has no deployed `IntentGatewayV2` instance yet, or
- has a deployment whose `NewDeployment` registration message has not yet been delivered/finalized cross-chain (exactly analogous to Chainlink upkeep still being "pending" registrar approval).

No solver can ever legitimately fill such an order (the destination gateway either doesn't exist or won't recognize itself as the counterpart), and no relayer/consensus-client infrastructure exists to deliver the eventual `RedeemEscrow`/fill message back to source. The user's escrowed `order.inputs` become effectively stuck: `cancelOrder` cross-chain paths (`_cancelFromSource`/`_cancelFromDest`) still assume a working consensus client and registered counterpart to prove non-fill or dispatch a refund message.

### Impact Explanation
Funds escrowed via `placeOrder` for an unregistered/not-yet-confirmed destination cannot be filled (no counterpart exists to fill against) and cannot be reliably recovered cross-chain (the cancellation path depends on the same missing infrastructure — consensus client, registered instance, and relayer). This is a permanent freezing-of-funds condition for the affected user's escrow, satisfying the "permanent freezing of funds" acceptance criterion. Given the trigger is a single unprivileged `placeOrder` transaction with a crafted or premature `destination`, severity is Medium, matching the original Chainlink report's Medium rating.

### Likelihood Explanation
Likelihood is realistic in the same window described in the original report: immediately after a new destination chain's gateway is deployed but before its `NewDeployment` registration message has been delivered and processed on other chains (or before the peer's own registration data propagates), any user (or a bot racing to be first) can place an order targeting that destination. There is no on-chain gate preventing this — the contract intentionally supports an "unknown chain" fallback fee path rather than reverting, which independently confirms the missing validation.

### Recommendation
In `placeOrder`, require that `order.destination` resolves via `instance(order.destination)` (i.e., a registered, confirmed peer gateway) before escrowing funds, reverting with `UnknownInstance` (or a similar explicit error) otherwise — mirroring the check already used elsewhere for cross-chain destination validation. This prevents orders from being created against destinations whose cross-chain registration/relayer infrastructure has not yet been confirmed.

### Proof of Concept
1. Deploy `IntentGatewayV2` on chain A with `initialize(params, peerChains=[])` (no peers registered), or with a peer set that does not yet include chain B.
2. Governance deploys the counterpart gateway on chain B and dispatches (but has not yet had delivered/processed) a `NewDeployment` message to register B with A.
3. Before that message is delivered/confirmed, a user calls `placeOrder(order, graffiti)` on chain A with `order.destination = StateMachine.evm(B)`, escrowing `order.inputs`.
4. `placeOrder` succeeds (as shown by `testPlaceOrderDestinationFeeWithFallback`, which places an order to an entirely unknown/never-registered `"UNKNOWN_CHAIN"` destination and only observes a fee fallback, not a revert): [6](#0-5) 
5. No solver on chain B recognizes the order (or chain B's gateway simply does not exist/does not name A as a peer), so `fillOrder` never succeeds; the cross-chain cancellation path likewise cannot complete without the corresponding consensus client/relayer infrastructure that depends on the same registration. The user's escrow in step 3 is stuck.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L105-127)
```text
    /**
     * @dev One-time init of a bare proxy: registers the peers, each bound to `address(this)`,
     * stores the params, arms the relayer gate, and lands at `VERSION`. Refused on any proxy
     * already at a version, see `onlyFresh`.
     * @param p The initial gateway configuration parameters.
     * @param peerChains State-machine ids of the cross-chain peers to register, each bound to this
     * gateway's own address so no peer address is carried in the proxy's init data.
     * @param relayer The only relayer whose deliveries are accepted. Zero leaves the gate open.
     */
    function initialize(Params memory p, bytes[] memory peerChains, address relayer)
        public
        onlyFresh
        reinitializer(VERSION)
    {
        uint256 peersLength = peerChains.length;
        for (uint256 i = 0; i < peersLength; i++) {
            Deployment memory deployment = Deployment({chain: peerChains[i], gateway: address(this)});
            _addDeployment(deployment);
        }
        _validateParams(p);
        _params = p;
        _setRelayer(relayer);
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L157-165)
```text
    /**
     * @dev Returns the registered gateway address for a given state machine.
     * Reverts with `UnknownInstance` if no remote deployment is registered.
     * @param stateMachineId The raw state machine identifier bytes.
     * @return The gateway address for the given state machine.
     */
    function instance(bytes calldata stateMachineId) public view returns (address) {
        return _instance(stateMachineId);
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-234)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3085-3127)
```text
    function testPlaceOrderDestinationFeeWithFallback() public {
        // Test that when destination fee is not set (or is 0), it falls back to default protocol fee
        IntentGatewayV2 customGateway = _deployGatewayProxy();
        Params memory customParams = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: 10000,
            protocolFeeBps: 100, // 1% default
            priceOracle: address(0)
        });
        customGateway.initialize(customParams, new bytes[](0), address(0));

        // Place order to destination without specific fee set
        uint256 inputAmount = 1000 * 1e6; // 1000 USDC
        uint256 expectedDefaultFee = (inputAmount * 100) / 10000; // 10 USDC (1% default)

        deal(address(usdc), user, inputAmount);

        bytes memory unknownDestination = bytes("UNKNOWN_CHAIN");

        Order memory order = Order({
            user: bytes32(0),
            source: bytes(""),
            destination: unknownDestination,
            deadline: block.timestamp + 1 hours,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: new TokenInfo[](1),
            output: PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: new TokenInfo[](1), call: ""})
        });

        order.inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});
        order.output.assets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 2000 * 1e18});

        vm.startPrank(user);
        usdc.approve(address(customGateway), inputAmount);

        vm.recordLogs();
        customGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-356)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
```
