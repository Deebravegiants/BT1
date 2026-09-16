### Title
Excess native token overpayment in `placeOrder` is permanently stuck (no refund) - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In the Tron variant of `IntentGatewayV2`, `placeOrder` accepts native token payments for order inputs, predispatch assets, and solver fees, tracking spend against a local `msgValue` counter. Unlike the canonical EVM `IntentGatewayV2.sol`, this Tron implementation never refunds any `msgValue` left over after all deductions. Any native token sent in excess of what is required to cover inputs, predispatch assets, and the fee-token swap is silently retained by the contract with no path for the depositor to reclaim it.

### Finding Description
`placeOrder` in `evm/tron/contracts/apps/IntentGatewayV2.sol` is `payable` and tracks native token consumption via a local `msgValue` variable that is decremented as it is spent on predispatch assets [1](#0-0) , on native-token inputs [2](#0-1) , and on the fee-token swap via `swapETHForExactTokens` [3](#0-2) . `swapETHForExactTokens` only spends the amount required to fill `order.fees` (input `msgValue`, not the full amount, is provided) and any unused wei from that call is refunded by the Uniswap router to `address(this)` (the gateway), not to the user.

The function then immediately emits `OrderPlaced` and returns without ever checking whether `msgValue > 0` and sending the remainder back to `msg.sender` [4](#0-3) .

This is in direct contrast to the mainline EVM contract, `evm/src/apps/IntentGatewayV2.sol`, which explicitly refunds any unspent native token to the caller at the end of `placeOrder`: `if (msgValue > 0) { _sendValue(msg.sender, msgValue); }` [5](#0-4) , and this refund behavior is explicitly tested for overpayment and fee-swap scenarios in `evm/tests/foundry/IntentGatewayV2SameChainTest.sol` and `evm/tests/foundry/IntentGatewayV2Test.sol` [6](#0-5) [7](#0-6) .

Because the Tron variant lacks this same refund step, any user who:
- sends `msg.value` slightly greater than the sum of native-token order inputs, or
- pays `order.fees` in native token via the Uniswap swap (which almost always leaves unspent wei, since `swapETHForExactTokens` only consumes what's needed to buy the exact fee amount, and users must overestimate `msg.value` to account for slippage/price movement),

will have the excess native token permanently locked in the `IntentGatewayV2` contract with no withdrawal function exposed to depositors. This mirrors the "user loses money on a failed/overpaid interaction with no refund path" bug class from the referenced report, but manifests as a silent stuck-fund condition rather than a reverting `require`.

### Impact Explanation
This is a concrete, permanent freezing-of-funds bug reachable by any unprivileged order placer (an "intent solver/user" actor explicitly in scope) on the Tron deployment of the intents system. Every native-token order placement that isn't penny-exact, and essentially every native-fee-paid order (since `swapETHForExactTokens` leaves a router refund of unused ETH sitting in the gateway rather than the user), results in unrecoverable user funds. There is no compensating `withdraw`/`sweep` function for the depositor visible in this contract region. Given normal user behavior (overestimating `msg.value` for slippage protection on the swap), this is not an edge case but the expected outcome for most native-token order placements — qualifying as High severity permanent loss of user funds.

### Likelihood Explanation
High likelihood: this triggers on the ordinary, non-malicious happy path any time a user places an order with native-token inputs and/or pays solver fees in native token, since users must send `msg.value` with headroom for the fee-swap slippage (`swapETHForExactTokens` guarantees exact output but variable, generally lower, input consumption). No adversarial setup or governance/relayer misbehavior is required.

### Recommendation
Add the same trailing refund present in the canonical EVM contract: after all native token deductions (predispatch, inputs, fee swap) track the remaining `msgValue` and, if greater than zero, send it back to `msg.sender` before emitting `OrderPlaced`, mirroring `evm/src/apps/IntentGatewayV2.sol` lines 394-397.

### Proof of Concept
1. User calls `placeOrder` on the Tron `IntentGatewayV2` with one ERC-20 input, `order.fees > 0`, and no `msg.value` earmarked input assets — but pays the fee in native token by sending `msg.value = X` where `X` comfortably covers `order.fees` after the swap.
2. `swapETHForExactTokens{value: msgValue}(order.fees, ...)` executes, spending only `amounts[0] <= msgValue` wei and refunding the difference to `address(this)` (the gateway contract), per standard Uniswap V2 router behavior.
3. `placeOrder` proceeds directly to `emit OrderPlaced(...)` and returns — the leftover ETH refunded to the contract in step 2 is never forwarded to `msg.sender`.
4. Repeat across users/orders: the gateway accumulates permanently stuck native token with no function to return it to the original depositors.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L398-403)
```text
                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L454-457)
```text
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L474-482)
```text
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L488-506)
```text
        }

        emit OrderPlaced({
            user: order.user,
            source: order.source,
            destination: order.destination,
            deadline: order.deadline,
            nonce: order.nonce,
            fees: order.fees,
            session: order.session,
            predispatch: order.predispatch.assets,
            inputs: reducedInputs,
            beneficiary: order.output.beneficiary,
            outputs: order.output.assets,
            predispatchCall: order.predispatch.call,
            outputCall: order.output.call,
            graffiti: graffiti
        });
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2312-2347)
```text
    /// @notice Excess msg.value beyond native input legs is refunded to the user.
    function testPlaceOrder_RefundsExcessNativeToken() public {
        uint256 inputAmount = 1 ether;
        uint256 overpayment = 0.5 ether;

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(0), amount: inputAmount}); // native ETH

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: 1000 * 1e6});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 100,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        uint256 userBalBefore = user.balance;

        vm.prank(user);
        intentGateway.placeOrder{value: inputAmount + overpayment}(order, bytes32(0));

        // User should only have spent inputAmount, overpayment refunded
        assertEq(user.balance, userBalBefore - inputAmount, "Overpayment should be refunded");
        assertEq(address(intentGateway).balance, inputAmount, "Gateway should only hold escrowed amount");
    }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3713-3750)
```text
    /// @notice placeOrder with fee swap refunds unused ETH after swapETHForExactTokens.
    function testPlaceOrder_FeeSwap_RefundsExcessNativeToken() public {
        uint256 inputAmount = 1000 * 1e6;
        uint256 feeAmount = 1 * 1e18; // 1 DAI worth of fees

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 1000,
            nonce: 0,
            fees: feeAmount,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        uint256 userEthBefore = user.balance;

        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        // Send 5 ETH for a fee swap that should cost much less
        intentGateway.placeOrder{value: 5 ether}(order, bytes32(0));
        vm.stopPrank();

        // User should get back most of the 5 ETH — the swap only needed a tiny fraction
        uint256 ethSpent = userEthBefore - user.balance;
        assertTrue(ethSpent < 1 ether, "User should have been refunded most of the 5 ETH");
```
