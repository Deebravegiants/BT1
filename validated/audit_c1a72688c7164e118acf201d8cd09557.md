### Title
EvmHost.dispatch()/fundRequest() strand excess ETH paid for relayer fees instead of refunding callers - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept native ETH to pay for the fee-token cost of a Hyperbridge request via `swapETHForExactTokens`, but none of them capture the swap's return value or refund any leftover ETH to the caller — the same bug class as the referenced Tokemak `LMPVaultRouterBase.mint()` report where unused `msg.value` is silently retained by the contract.

### Finding Description
In each of these functions, the entire `msg.value` is forwarded to the Uniswap V2 router with an exact-output swap targeting only `post.fee` / `get.fee` / `amount` worth of fee tokens: [1](#0-0) [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` is an exact-output swap, so it only spends the ETH required to obtain `post.fee`/`get.fee`/`amount` tokens and refunds any unspent ETH to its caller — which in this case is `EvmHost` itself, not the original transaction sender. This is confirmed by the wrapper implementations used behind `IUniswapV2Router02`, e.g. `UniV3UniswapV2Wrapper.swapETHForExactTokens` and `UniV4UniswapV2Wrapper.swapETHForExactTokens`, both of which compute `spent`/`refundETH` and send the unspent ETH back to `msg.sender` (i.e., `EvmHost`): [4](#0-3) [5](#0-4) 

None of the three `EvmHost` functions capture this refunded ETH or forward it back to `_msgSender()`. The refunded amount lands in `EvmHost`'s own balance and there is no mechanism in these functions (nor return-value handling) to reconcile or return it — so any user who overestimates the native amount needed to cover the fee-token swap (which is expected, since the exact ETH cost of an exact-output swap can't be known precisely in advance due to slippage/price movement) permanently loses the difference.

This differs from the codebase's other ETH-handling paths (`IntentGatewayV2`, `ExtrinsicIntents`, `WrappedHyperFungibleToken`), which explicitly track `msgValue` after swaps and refund any unspent native amount to `msg.sender`/`beneficiary`: [6](#0-5) [7](#0-6) 

### Impact Explanation
Any relayer, app, or end user dispatching a POST/GET request or topping up a request's fee via `fundRequest()` with native ETH loses any ETH beyond the exact amount consumed by the fee-token swap. This is a direct, permanent loss of user funds with no recovery path in these functions — matching "concrete theft or permanent freezing of funds" criteria. Given `dispatch()` is the primary entrypoint used by every app built on Hyperbridge (message dispatchers, token bridges, intents) whenever they choose to pay in native token, the blast radius spans the entire ecosystem of native-fee-paying callers.

### Likelihood Explanation
High likelihood: this triggers on any call that pays fees in native token and doesn't send the exact minimal amount required by the swap (which is the normal case, since callers typically pad `msg.value` for slippage safety, exactly as described in the original Tokemak report). No malicious actor is required — normal usage patterns reliably lose funds.

### Recommendation
Capture the `amounts` array returned by `swapETHForExactTokens` in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, compute `msg.value - amounts[0]` as the unspent portion, and refund it to `_msgSender()` (or `post.payer`/`get`'s payer) via a low-level call, mirroring the pattern already used in `ExtrinsicIntents.sol` and `IntentGatewayV2.sol`.

### Proof of Concept
1. Caller estimates fee-token cost `X` for `post.fee` and calls `dispatch{value: X * 1.5}(post)` to account for price slippage.
2. `EvmHost.dispatch` forwards the full `1.5X` ETH to `swapETHForExactTokens(post.fee, ...)`.
3. The Uniswap wrapper spends only `~X` ETH (or less, depending on price) to fill the exact-output order and refunds `~0.5X` ETH back to `EvmHost` via `msg.sender.call{value: refund}("")`.
4. `EvmHost.dispatch` never reads or forwards this refund; it is retained permanently in the `EvmHost` contract's balance.
5. The caller has irrecoverably lost `~0.5X` ETH with no function in `EvmHost.sol` to reclaim it back to the original payer.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L203-217)
```text
        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
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
