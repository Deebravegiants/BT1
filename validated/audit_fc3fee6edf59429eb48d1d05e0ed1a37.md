### Title
Excess native ETH sent to `EvmHost.dispatch()`/`fundRequest()` is permanently stuck instead of refunded - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native ETH via `msg.value` and swap it for the exact fee-token amount needed using Uniswap's `swapETHForExactTokens`, but never refund the unused ETH dust back to the original caller, mirroring the Allo.sol pool-creation bug where overpaid funds are silently absorbed by the contract.

### Finding Description
In `dispatch(DispatchPost)`, when `msg.value > 0`, the whole `msg.value` is forwarded to the router: [1](#0-0) 

Standard `UniswapV2Router02.swapETHForExactTokens` only consumes the exact ETH needed for `post.fee` tokens and refunds any dust ETH to `msg.sender` of that call — which is `EvmHost` itself, not the end user who invoked `dispatch()`. `EvmHost` never forwards that refunded dust back to the original caller (no `_msgSender().call{value: ...}` after the swap), so the excess ETH is retained inside the `EvmHost` contract balance permanently. The exact same pattern (send full `msg.value` to the router, no post-swap refund) also exists in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest()`: [3](#0-2) 

This is functionally identical to the reported Allo.sol bug class: a user who sends more native value than strictly required for the fee gets no refund of the remainder, and the excess is effectively lost by the caller. By contrast, other in-scope contracts in the same repo correctly implement refund logic for this exact scenario, confirming the expected pattern was simply omitted in `EvmHost`. `IntentGatewayV2._fillOrder`/`placeOrder` explicitly track `amounts[0]` returned by the swap and refund the difference to `msg.sender`: [4](#0-3) 

Foundry tests even codify this refund expectation for `IntentGatewayV2`: [5](#0-4) 

`EvmHost.dispatch`/`fundRequest` has no analogous refund step, so any dApp or user relying on the documented "send native ETH, host swaps it for you" flow (as described in the docs) will lose any overpayment.

### Impact Explanation
Any unprivileged caller (an application contract or an end user submitting a POST/GET request or funding a pending request) who overestimates the ETH needed to cover `post.fee`/`get.fee`/`amount` in fee-token terms permanently loses the difference — the ETH is absorbed into `EvmHost`'s balance with no path for recovery to the payer (no `withdraw` function was found that returns funds to the original sender; any admin/host-manager withdrawal would only benefit the protocol treasury, not the user). This is a direct loss-of-funds condition reachable from a single `dispatch()`/`fundRequest()` call, satisfying "concrete theft or permanent freezing of funds" for message dispatchers.

### Likelihood Explanation
Because Uniswap swap output amounts (and thus required ETH input) fluctuate with pool price between the time a fee is estimated off-chain (`quote()`) and the transaction's execution, and because the docs explicitly instruct users to just "send enough native tokens," some overpayment margin is a normal/expected usage pattern (as evidenced by the buffer logic in `HyperbridgeLzEndpoint.quote()`, which doubles the fee estimate specifically to account for slippage). This makes the bug highly likely to trigger in normal operation, not just as an edge case.

### Recommendation
After each `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the `amounts` array returned by the router and refund any leftover ETH (`msg.value - amounts[0]`) back to `_msgSender()`, mirroring the pattern already used in `IntentGatewayV2`.

### Proof of Concept
1. Caller estimates `post.fee` fee-token cost and computes the ETH needed via `quote()`, but adds a safety margin (or the pool price is more favorable at execution time), sending `msg.value = X` where `X` exceeds the ETH actually required.
2. `EvmHost.dispatch(DispatchPost)` calls `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)`.
3. Uniswap's router consumes only `amountIn <= X` and refunds `X - amountIn` ETH to `msg.sender`, i.e., to `EvmHost`.
4. `EvmHost` never forwards this `X - amountIn` refund to the original caller; it silently accrues in the `EvmHost` contract balance.
5. The caller has permanently lost `X - amountIn` ETH with no function available to reclaim it.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-932)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L974-985)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L1031-1042)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L375-397)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }

        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
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
