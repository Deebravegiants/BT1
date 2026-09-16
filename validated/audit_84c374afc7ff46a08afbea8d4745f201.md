### Title
Excess native token sent to `EvmHost.dispatch()` / `fundRequest()` is not refunded to the caller and is trapped in the contract - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token payment and swap it into the fee token via `swapETHForExactTokens`, but none of them refund unused native token back to the caller after the swap.

### Finding Description
When a caller pays for message dispatch with native token, `EvmHost.dispatch(DispatchPost)` forwards the full `msg.value` into the Uniswap router: [1](#0-0) 

The same pattern is repeated in `dispatch(DispatchGet)`: [2](#0-1) 

and in `fundRequest()`: [3](#0-2) 

`swapETHForExactTokens(amountOut, path, to, deadline)` only consumes the amount of ETH necessary to buy exactly `post.fee` (or `amount`) worth of `feeToken`. Any leftover ETH from `msg.value` is refunded by the router logic to *its own caller* — i.e., to `EvmHost` itself, not to the original transaction sender (`_msgSender()`). This is confirmed by the standard `IUniswapV2Router02.swapETHForExactTokens` refund behavior, which this codebase's own fork test exercises directly against the configured router: [4](#0-3) 

Once the dust ETH lands back in `EvmHost`, `EvmHost` has no logic in `dispatch`/`fundRequest` to relay it back to `_msgSender()`. The only way to move it out is the governance-restricted `withdraw()` function: [5](#0-4) 

which can only be invoked by `_hostParams.hostManager` (cross-chain governance), not by the original caller who overpaid.

This is the exact bug class from the reported Footium issue: a function that accepts `msg.value` for a fee, but does not refund the excess to `msg.sender`, causing user funds to be permanently stuck. Notably, this codebase demonstrates that the pattern is *known and expected to be fixed* elsewhere — `IntentGatewayV2.placeOrder`/`fillOrder` and `ExtrinsicIntents._fillCrossChain` explicitly track leftover `msgValue` after the swap and refund it via `_sendValue(msg.sender, msgValue)`: [6](#0-5) [7](#0-6) 

`EvmHost.sol` — the core dispatcher reachable by any unprivileged app or user relaying a POST/GET request or funding one — is missing this same refund logic.

### Impact Explanation
Any caller (an app contract or an end user) who dispatches a POST/GET request or calls `fundRequest` with native token and supplies more ETH than the swap actually needs (a very likely scenario in practice, since callers must over-provision `msg.value` to guard against slippage/price movement in the Uniswap quote) permanently loses the difference. The ETH is not burned, but it becomes indistinguishable protocol-level revenue recoverable only through cross-chain governance's `withdraw()`, never by the original payer. This is a permanent loss of user funds for anyone using the native-token payment path of `IDispatcher.dispatch`/`fundRequest`, which per the project's own documentation is a first-class, officially supported payment method.

### Likelihood Explanation
High likelihood of occurrence: the documented usage pattern explicitly tells integrators to estimate the native fee off-chain via `quote()` and this quote is inherently imprecise/sandwich-able, meaning users will routinely send more ETH than strictly required to avoid reverts. Every such overpayment silently strands funds in the host contract.

### Recommendation
After performing `swapETHForExactTokens{value: msg.value}(...)` in `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the returned `amounts[0]` (actual ETH spent) and refund `msg.value - amounts[0]` back to `_msgSender()`, mirroring the pattern already implemented in `IntentGatewayV2.sol` and `ExtrinsicIntents.sol`.

### Proof of Concept
1. User calls `EvmHost.dispatch(DispatchPost)` with `post.fee = 100` (fee-token units) and sends `msg.value = 1 ether`, intending to cover slippage on the ETH/feeToken pool.
2. `EvmHost` calls `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: 1 ether}(100, path, address(this), block.timestamp)`.
3. The router only needs, say, `0.01 ether` to buy `100` fee tokens; it refunds `0.99 ether` back to `msg.sender` of the swap call, which is `EvmHost`.
4. `EvmHost.dispatch` returns without forwarding any of that `0.99 ether` back to the user.
5. The user's `0.99 ether` is now stuck in `EvmHost`'s balance, only movable by `hostManager.withdraw()` — never back to the user.

### Citations

**File:** evm/src/core/EvmHost.sol (L651-660)
```text
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
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

**File:** evm/tests/foundry/ConfiguredWrapperForkTest.t.sol (L41-59)
```text
        IUniswapV2Router02 router = IUniswapV2Router02(config.get("UNISWAP_V2").toAddress());
        address feeToken = config.get("FEE_TOKEN").toAddress();
        address weth = router.WETH();

        // ~1 unit of the fee token (e.g. 1 USDC / 1 USDT / 1 WXDAI).
        uint256 amountOut = 10 ** IERC20Metadata(feeToken).decimals();

        address[] memory path = new address[](2);
        path[0] = weth;
        path[1] = feeToken;

        uint256 budget = 100 ether; // generous amountInMaximum; the wrapper refunds the excess
        vm.deal(address(this), budget);

        uint256 balanceBefore = IERC20(feeToken).balanceOf(address(this));
        router.swapETHForExactTokens{value: budget}(amountOut, path, address(this), block.timestamp + 1 hours);
        uint256 received = IERC20(feeToken).balanceOf(address(this)) - balanceBefore;

        assertGe(received, amountOut, "configured uniswapV2 did not deliver the fee token");
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L204-217)
```text
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
