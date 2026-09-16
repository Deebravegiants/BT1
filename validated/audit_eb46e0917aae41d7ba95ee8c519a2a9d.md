### Title
Excess native `msg.value` in `EvmHost.dispatch`/`fundRequest` is swapped and trapped in the host contract instead of refunded to the caller - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept native token payment and convert it to `feeToken` via `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`. Uniswap V2's `swapETHForExactTokens` only spends up to `amounts[0]` ETH and refunds any unspent ETH — but the refund is sent to `msg.sender` as seen by the router call, which is the `EvmHost` contract itself, not the original transaction sender who supplied the excess `msg.value`. Any overpayment above the exact ETH cost of the swap is therefore absorbed into the `EvmHost` contract balance rather than returned to the payer. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
Every call site that dispatches with native token payment forwards the entire `msg.value` into `swapETHForExactTokens`, requesting only `post.fee` / `get.fee` / `amount` worth of `feeToken`, with the router's `to` address set to `address(this)` (the `EvmHost`):

```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
```

The Uniswap V2 Router's `swapETHForExactTokens` implementation computes the required input amount and, if `msg.value` exceeds it, refunds the difference to `msg.sender` — but that `msg.sender` is the caller of the router function, i.e., `EvmHost`, not the end user who called `dispatch()`/`fundRequest()` on `EvmHost`. Consequently:
- The refunded ETH lands in `EvmHost`'s own balance.
- The user who overpaid never gets the excess back through this dispatch flow.

This is functionally identical to the referenced Sherlock finding: a contract accepts a payment (`msg.value`) that can exceed the required amount, and the excess is not returned to the payer, resulting in a fund loss for the caller. Documentation for these functions explicitly states "Will revert if enough native tokens are not provided," implying an expectation of exact-or-more sizing by callers, but nothing in the code path returns the "more" portion to the caller. [4](#0-3) 

By contrast, other parts of the same codebase (the Intents module) explicitly implement and test refunding of native-token overpayment for exactly this class of bug — e.g., `IntentsBase._sendValue` refund logic and `IntentGatewayV2SameChainTest.testPlaceOrder_RefundsExcessNativeToken` / `testPlaceOrder_FeeSwap_RefundsExcessNativeToken`, which assert that unspent ETH after `swapETHForExactTokens` swaps is returned to the original payer. [5](#0-4)  This confirms the pattern is a known, expected safeguard elsewhere in the protocol, but it is missing from `EvmHost.dispatch`/`fundRequest`.

### Impact Explanation
Any unprivileged user or application dispatching a POST/GET request or funding a pending request with native token payment (a very common, directly documented usage pattern per `post-requests.mdx`/`get-requests.mdx`/`idispatcher.mdx`) risks having any overpaid ETH permanently stuck in the `EvmHost` contract rather than returned. Given ETH price volatility and the difficulty of quoting an exact Uniswap V2 swap amount client-side ahead of transaction execution (slippage, price movement between quote and execution), overpayment by well-meaning callers is a realistic, frequent occurrence, not an edge case. This constitutes a direct, permanent loss of user funds through the primary message-dispatch entry point of the protocol.

### Likelihood Explanation
High likelihood: this is the standard/documented way to pay dispatch fees in native token, used by any relayer, app, or user calling `dispatch{value: ...}(...)`. Client-side fee estimation is inherently approximate versus the exact AMM execution price, so it is common practice (and shown in the docs' "Estimating Fees" section) for callers to send a buffer above the estimated fee. Every native-fee dispatch or fund-request call is exposed to this loss.

### Recommendation
After the `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, compute any leftover native balance attributable to the overpayment (e.g., track `address(this).balance` before/after, or use `swapETHForExactTokens`'s returned `amounts[0]` to determine `msg.value - amounts[0]`) and refund it to `_msgSender()` (or the designated `payer`), mirroring the pattern already implemented and tested in `IntentsBase`/`IntentGatewayV2`.

### Proof of Concept
1. Caller estimates the fee-token cost of `post.fee` in native ETH client-side, then calls:
   ```solidity
   host.dispatch{value: estimatedEthCost + buffer}(DispatchPost({... fee: relayerFee ...}));
   ```
2. Inside `dispatch`, `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` executes; because ETH price moved favorably or the buffer was generous, the actual ETH needed is less than `msg.value`.
3. Uniswap V2 Router refunds `msg.value - amounts[0]` to `msg.sender` of the swap call, which is `address(EvmHost)`.
4. The caller's transaction returns successfully with `commitment`, but the caller's ETH balance is now reduced by the full `msg.value` sent, not just the actual swap cost — the difference sits in `EvmHost`'s balance instead of being returned to the caller (contrast with `IntentGatewayV2SameChainTest.testPlaceOrder_RefundsExcessNativeToken`, which shows the expected/refunded behavior implemented elsewhere in the same codebase). [6](#0-5)

### Citations

**File:** evm/src/core/EvmHost.sol (L908-920)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * @param post - post request
     * @return commitment - the request commitment
     */
```

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
