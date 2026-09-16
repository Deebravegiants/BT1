### Title
Missing native-token refund in `IntentGatewayV2.placeOrder()` permanently locks overpaid ETH - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder()` fails to refund unspent `msg.value` after escrowing inputs and paying fees, unlike the canonical EVM implementation of the same function. Any native token sent in excess of what is consumed by native-token inputs and fee swaps is silently trapped in the contract forever.

### Finding Description
`placeOrder()` is `payable` and accepts a mix of ERC20 and native-token inputs in the same call, tracking a running `msgValue` counter that is decremented as native legs are consumed [1](#0-0) . Native inputs decrement `msgValue` by the exact required amount [2](#0-1) , and if `order.fees > 0`, any remaining `msgValue` is consumed via a Uniswap swap to the fee token, but the returned swap output amount is not subtracted from `msgValue` and the leftover is never used again [3](#0-2) . After this block, the function proceeds directly to `emit OrderPlaced(...)` and returns, with no path that returns unspent `msgValue` to `msg.sender` [4](#0-3) .

This is the same bug class as the LineLib.sol finding cited in the report: two different transfer mechanisms (ERC20 `safeTransferFrom` vs. native `msg.value`) are handled asymmetrically within one function, and value sent via the "wrong"/unconsumed channel is silently absorbed by the contract with no way for the user to recover it.

The mainline EVM `IntentGatewayV2.sol` correctly guards against this exact scenario with an explicit refund step immediately after the fee-escrow block: `if (msgValue > 0) { _sendValue(msg.sender, msgValue); }` [5](#0-4) , and this behavior is covered by dedicated tests (`testPlaceOrder_RefundsExcessNativeToken`, `testPlaceOrder_ExactNativeToken_NoRefundNeeded`) [6](#0-5) . The Tron fork of the contract is missing this equivalent refund logic, indicating it diverged from the audited/patched mainline implementation.

### Impact Explanation
Any user who calls `placeOrder()` on the Tron `IntentGatewayV2` with:
- an ERC20-only order but attaches `msg.value > 0` (e.g., wallet UI defaults, accidental overpayment, or fee estimation drift), or
- a native-token input/fee leg but sends more native token than strictly required (e.g. to cover gas price uncertainty or Uniswap slippage)

will have the excess native token permanently locked in the `IntentGatewayV2` contract, with no owner-only sweep/rescue mechanism identified for this case. This is a direct, permanent loss of user funds (concrete freezing of funds), matching the "unbacked/locked funds" impact bar.

### Likelihood Explanation
Likelihood is high: `placeOrder()` is the primary unprivileged entry point reachable by any user submitting an order/intent, exactly the "intents escrow" surface called out as in-scope. Overpayment of native gas/fee tokens is a routine, easily-triggered user error (front-ends commonly pad `msg.value` for gas-price/slippage buffers), requiring no attacker and no special preconditions beyond `order.fees > 0` or an ERC20-only order with any `msg.value`.

### Recommendation
Mirror the canonical EVM implementation: after the fee-escrow block, add
```solidity
if (msgValue > 0) {
    (bool sent,) = msg.sender.call{value: msgValue}("");
    if (!sent) revert InsufficientNativeToken();
}
```
and additionally track/subtract the actual amount consumed by `swapETHForExactTokens` (its return value) from `msgValue`, since currently the full `msgValue` is passed to the swap without accounting for the amount actually spent, which the mainline code correctly does (`msgValue -= amounts[0];`) [7](#0-6)  — the Tron version omits this too [8](#0-7) .

### Proof of Concept
1. Deploy/observe the Tron `IntentGatewayV2` with `order.fees > 0` and `_hostParams.uniswapV2` configured.
2. User calls `placeOrder{value: X}(order, graffiti)` where `order.inputs` are all ERC20 tokens (no `token == address(0)` legs), so the entire `msgValue = X` is untouched through the input-escrow loop [2](#0-1) .
3. In the fee block, `swapETHForExactTokens{value: msgValue}(order.fees, ...)` is invoked with the full `msgValue`, refunding any Uniswap-router-side leftover to `address(this)` (the gateway), not the user, and the local `msgValue` variable is never decremented nor refunded [8](#0-7) .
4. Function completes and emits `OrderPlaced` without returning any native token to `msg.sender` [9](#0-8) .
5. The user's excess ETH remains stuck in the `IntentGatewayV2` contract balance, unrecoverable through any user-facing function.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L388-388)
```text
        uint256 msgValue = msg.value;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-460)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L383-386)
```text
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
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
