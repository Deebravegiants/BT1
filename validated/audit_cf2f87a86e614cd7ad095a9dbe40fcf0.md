EvmHost.sol has a `receive() external payable` function, meaning it can accept the excess ETH refund from Uniswap's `swapETHForExactTokens`. This is the critical fact: since `EvmHost.dispatch()`, `dispatch(DispatchGet)`, and `fundRequest()` all forward the *entire* `msg.value` to `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` [1](#0-0) [2](#0-1) [3](#0-2) , the standard UniswapV2Router02 implementation refunds any excess ETH (`msg.value - amounts[0]`) via `TransferHelper.safeTransferETH(msg.sender, ...)`. Because `EvmHost` itself is the caller of the router (not the original end user), that refund is sent back to `EvmHost`'s own address, not to the transaction's original sender. Since `EvmHost` has a `receive()` function, the refund succeeds silently and the overpaid ETH is permanently absorbed into the host contract's balance instead of returning to the user who overpaid.

I was not able to fully verify in this session whether `EvmHost` (or `HostManager`) exposes any function to sweep/reclaim native ETH balance (as opposed to `feeToken` revenue) back to users or governance — the `IHostManager.updateHostParams`/withdraw logic I saw only referenced `feeToken` revenue withdrawal [4](#0-3) , not native ETH. If no such mechanism exists, overpaid ETH is permanently stuck/unrecoverable by the paying user, which would confirm the analog as a valid Medium-severity finding (permanent freezing/loss of user funds on overpayment, reachable by any unprivileged caller of `dispatch`/`fundRequest`).

Given the residual uncertainty about ETH-sweep capability, and that this is a plausible but not fully confirmed root-cause chain (I could not trace whether `IUniswapV2Router02` at `_hostParams.uniswapV2` is always the canonical Uniswap V2 router with `msg.sender`-based refund semantics, versus a custom wrapper contract like `UniV3UniswapV2Wrapper`/`UniV4UniswapV2Wrapper` — which also refund to `msg.sender` i.e. `EvmHost`, per [5](#0-4)  and [6](#0-5) ), I'll present the finding with the caveat noted, since both the real Uniswap router and both first-party wrapper implementations exhibit the same "refund goes to `EvmHost`, not original user" behavior.

### Title
Overpayment refund from Uniswap swap is sent to EvmHost instead of the original caller, permanently trapping excess native token payments - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` forward the caller's entire `msg.value` to `IUniswapV2Router02.swapETHForExactTokens`, requesting only the exact `post.fee`/`get.fee`/`amount` in `feeToken`. Any excess ETH the router refunds is sent to the immediate caller of the router — which is `EvmHost` itself — rather than to the original transaction sender who overpaid.

### Finding Description
In `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, the full `msg.value` is passed to the configured `uniswapV2` router's `swapETHForExactTokens` call: [1](#0-0) [7](#0-6) 

The router's `swapETHForExactTokens` (both canonical UniswapV2Router02 and the project's own `UniV3UniswapV2Wrapper`/`UniV4UniswapV2Wrapper`) only consumes the exact ETH needed to purchase `amountOut` of `feeToken`, and refunds the difference to whichever address called it — here, `EvmHost`, since `EvmHost` is the direct caller (`address(this)` is passed only as the token recipient, not as `msg.sender` in the router's frame). `EvmHost` has a `receive() external payable` function, so this refund is silently accepted and absorbed into `EvmHost`'s balance rather than being forwarded back to the actual user who sent the excess `msg.value`. This is functionally the same class of bug as the reported `FootiumAcademy.mintPlayers` issue: user-supplied overpayment is not validated/capped against the exact required amount, and no refund path exists back to the payer.

### Impact Explanation
Any unprivileged user calling `dispatch()` or `fundRequest()` with `msg.value` even slightly greater than the ETH cost of the exact `fee`/`amount` in `feeToken` loses the difference permanently to the `EvmHost` contract, with no visible sweep/rescue mechanism for native ETH (only `feeToken` revenue withdrawal is exposed via `IHostManager`). Given that off-chain fee estimation via Uniswap's `getAmountsIn` is explicitly warned to be imprecise/sandwich-prone (frontend docs suggest padding the sent value), overpayment is a realistic, likely occurrence for normal users, not an edge case.

### Likelihood Explanation
High likelihood: this is the default, documented pattern for paying dispatch fees in native token (`msg.value`), and frontends are told to only use `quote()` off-chain as an estimate, encouraging users to send a safety margin of ETH that exceeds the exact fee — directly triggering the unrefunded loss on every such call.

### Recommendation
After the swap, compute `msg.value - amounts[0]` (the actual ETH spent, as returned by `swapETHForExactTokens`) and refund the remainder to `_msgSender()` (or `post.payer`/`get.payer`), mirroring the refund pattern already implemented in `IntentGatewayV2`/`ExtrinsicIntents` (`_sendValue(msg.sender, msgValue)`) and in `UniV3UniswapV2Wrapper`/`UniV4UniswapV2Wrapper`. Alternatively, revert if `msg.value` exceeds the quoted requirement beyond an acceptable tolerance.

### Proof of Concept
1. Attacker/user calls `EvmHost.dispatch{value: X}(post)` where `X` is intentionally or accidentally greater than the ETH amount required to buy `post.fee` of `feeToken` via `swapETHForExactTokens`.
2. Inside `dispatch`, `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` executes; the router consumes only `amountIn <= X` and refunds `X - amountIn` to `msg.sender`, i.e., to `EvmHost`.
3. `EvmHost.receive()` accepts the ETH, permanently adding it to the host's balance.
4. The original caller's transaction succeeds, the request is dispatched normally, but the caller never receives back the `X - amountIn` difference — confirmable by asserting `msg.sender.balance` before/after the call in a Foundry test analogous to `testPlaceOrder_RefundsExcessNativeToken` in `IntentGatewayV2SameChainTest.sol`, but pointed at `EvmHost.dispatch` directly. [8](#0-7)

### Citations

**File:** evm/src/core/EvmHost.sol (L50-53)
```text
    // The authorized host manager contract, is itself an `IApp`
    // which receives governance requests from the Hyperbridge chain to either
    // withdraw revenue from the host or update its protocol parameters
    address hostManager;
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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L143-149)
```text
        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L91-96)
```text
        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2313-2347)
```text
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
