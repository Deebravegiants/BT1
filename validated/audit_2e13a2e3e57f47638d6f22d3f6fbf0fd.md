### Title
Excess native ETH sent to `EvmHost.dispatch()` / `fundRequest()` is not refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token payment and swap it for the exact fee-token amount needed via Uniswap V2's `swapETHForExactTokens`, but never refund the leftover ETH to the original caller.

### Finding Description
When a user pays for message dispatch with native tokens, `EvmHost` calls Uniswap's router with the full `msg.value`: [1](#0-0) 

`swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` only consumes the ETH required to obtain `post.fee` fee tokens. Per Uniswap V2 Router02 semantics, any unused ETH sent to `swapETHForExactTokens` is refunded to `msg.sender` of that call — but `msg.sender` from the router's perspective is `EvmHost` itself (since `EvmHost` is the direct caller), not the original external account that called `dispatch()`. The same pattern exists in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest()`: [3](#0-2) 

In all three functions, any excess `msg.value` beyond what's needed to purchase `post.fee`/`get.fee`/`amount` fee tokens is refunded by the router back into `EvmHost`'s own balance instead of being returned to `_msgSender()`. There is no subsequent logic in any of these functions that forwards the refunded ETH back to the caller, and no user-facing `withdraw`/`recover` function was found in `EvmHost.sol` that would let the original depositor reclaim these stray funds. This is a real design gap: any application contract or EOA (via an app contract, since EOAs shouldn't call directly per docs) that overestimates the ETH needed for a `dispatch()` or `fundRequest()` call permanently loses the excess into the `EvmHost` contract balance.

This is essentially the same bug class as the referenced Footium report — an unprivileged caller sends more native value than required for the operation and the excess is trapped rather than refunded — mapped onto Hyperbridge's core dispatch path, which is directly reachable by any relayer, application, or bandwidth purchaser calling `IDispatcher.dispatch`/`fundRequest`.

Notably, this exact overpayment-refund problem was identified and fixed elsewhere in the codebase (`IntentGatewayV2`), which explicitly tracks and refunds unspent native ETH after its own `swapETHForExactTokens` calls, as shown by dedicated tests: [4](#0-3) 

This confirms the team is aware of the overpayment-refund pattern needed around `swapETHForExactTokens`, but the fix was not applied to `EvmHost.dispatch`/`fundRequest`.

### Impact Explanation
Users/applications that pay dispatch or relayer-funding fees in native token and slightly overestimate the required ETH (which is common, since exact Uniswap pricing at execution time is unpredictable due to slippage/MEV) permanently lose the difference — it becomes stuck in the `EvmHost` contract with no recovery mechanism for the original payer. Given `dispatch()`/`fundRequest()` are the primary payment entry points for every cross-chain message on every EVM deployment of Hyperbridge, this can affect a large volume of transactions and result in a continuous, protocol-wide loss of user funds.

### Likelihood Explanation
High likelihood of occurrence: native-ETH payment is a documented, first-class payment method for `dispatch()` and `fundRequest()`, and callers must estimate `post.fee`/`get.fee` in fee-token terms then send enough ETH to cover a live Uniswap swap — over-provisioning ETH to guard against price movement/slippage is standard practice for callers, making overpayment routine rather than an edge case.

### Recommendation
After calling `swapETHForExactTokens`, capture the actual ETH spent (or track `address(this).balance` before/after) and refund any leftover ETH to `_msgSender()` (or an explicit `payer`/`refundTo` field on the request struct), mirroring the refund pattern already implemented in `IntentGatewayV2`.

### Proof of Concept
1. Caller estimates `post.fee = 100` fee-tokens is needed and, to be safe against slippage, sends `msg.value = 1 ether` to `EvmHost.dispatch(DispatchPost)`.
2. Inside `dispatch()`, `swapETHForExactTokens{value: 1 ether}(100, path, address(this), block.timestamp)` only spends e.g. `0.01 ether` to acquire the 100 fee tokens; the router refunds the remaining `0.99 ether` to `msg.sender`, which is `EvmHost`.
3. `EvmHost`'s ETH balance increases by `0.99 ether`, but no code path returns this to the original caller.
4. The caller has permanently lost `0.99 ether` with no way to recover it via any function on `EvmHost`.

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
