Confirmed: the Tron variant of `IntentGatewayV2.placeOrder()` is missing the native-token refund step that exists in the canonical EVM version. This is a valid analog to the reported bug class (native value getting permanently stuck when not consumed).

### Title
Missing native-token overpayment refund in `IntentGatewayV2.placeOrder()` permanently locks user ETH/TRX - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron deployment of the IntentGateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) omits the "refund unspent native tokens" step that the canonical EVM implementation (`evm/src/apps/IntentGatewayV2.sol`) performs at the end of `placeOrder()`. Any native value sent by the user beyond what is consumed by native-token inputs and the fee swap is silently retained by the contract with no accounting or withdrawal path.

### Finding Description
In `evm/src/apps/IntentGatewayV2.sol`, `placeOrder()` tracks the running `msgValue` as it consumes native tokens for inputs (`address(0)` legs) and for the optional fee swap, then explicitly refunds any leftover: [1](#0-0) 

The Tron variant implements the identical `msgValue` bookkeeping logic — decrementing `msgValue` for native inputs at [2](#0-1)  and for the fee-token swap at [3](#0-2) , but the function returns straight to `emit OrderPlaced(...)` without ever refunding the remaining `msgValue` to `msg.sender`: [4](#0-3) 

This is the same bug class as the referenced FEYTraderJoeProduct report: whenever `msg.value` is not fully equal to the sum consumed by the code path (e.g. the user only has ERC20 inputs and pays `order.fees` via fee-token but mistakenly/necessarily attaches extra native value, sends slightly more native than the exact native input amount, or the fee swap via Uniswap consumes less than the full `msgValue`), the surplus native value is stranded in the contract balance with no tracked owner and no withdrawal mechanism exposed to the user.

### Impact Explanation
Any unspent native value sent to `placeOrder` becomes permanently unrecoverable for the user — a direct freezing-of-funds bug reachable by a single unprivileged `placeOrder` transaction. This matches the "concrete... permanent freezing of funds" acceptance criterion. The contract's own test suite for the EVM version explicitly validates that overpaid native tokens must be refunded (`testPlaceOrder_RefundsExcessNativeToken`, `testPlaceOrder_FeeSwap_RefundsExcessNativeToken`) confirming this is intended, security-relevant behavior that the Tron port fails to replicate: [5](#0-4) [6](#0-5) 

### Likelihood Explanation
High likelihood: any caller who pays `order.fees` with native value (the documented, supported flow) but overestimates the swap cost, or who places an order with only ERC20 inputs but still attaches `msg.value` for the fee swap, will unavoidably leave dust or larger surplus stuck since Uniswap's `swapETHForExactTokens` typically consumes less than the full amount supplied. No malicious actor is required — normal usage triggers the loss.

### Recommendation
Port the missing refund step from the canonical EVM `IntentGatewayV2.sol` into the Tron variant: after all native-token consuming branches (predispatch, inputs, and fee swap) at the end of `placeOrder()`, add `if (msgValue > 0) { _sendValue(msg.sender, msgValue); }` before/at the `OrderPlaced` emission.

### Proof of Concept
1. User calls `placeOrder` on the Tron `IntentGatewayV2` with `order.inputs` containing only ERC20 tokens (no native leg) and `order.fees > 0`.
2. User attaches `msg.value = X` intending to pay the fee via native-to-feeToken swap through `swapETHForExactTokens{value: msgValue}(order.fees, ...)` at line 480.
3. `swapETHForExactTokens` only consumes the exact input amount needed to buy `order.fees` worth of fee tokens (typically `< X`), leaving `msgValue - amountIn > 0` unspent (variable `msgValue` in `evm/tron/contracts/apps/IntentGatewayV2.sol` is never decremented by the actual swap input and never refunded).
4. Function proceeds directly to `emit OrderPlaced(...)` and returns; the leftover native value remains in the contract's balance with no corresponding escrow entry and no way for `msg.sender` to reclaim it.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L393-397)
```text

        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-460)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-506)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3713-3752)
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
        assertTrue(ethSpent > 0, "User should have spent some ETH on the fee swap");
    }
```
