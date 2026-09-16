### Title
Excess native token overpayment to `EvmHost.dispatch()`/`fundRequest()` is permanently locked in the Host contract instead of being refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token payment and swap it into the `feeToken` via `swapETHForExactTokens`, but never capture the `amounts` array returned by the router and never refund any unused native token to the original caller. This is the same root-cause bug class as the external report's LayerZero refund issue: excess/unused value sent by a user for a cross-chain protocol fee is refunded by the downstream swap/endpoint to the immediate caller contract (`EvmHost` itself, since it is the one invoking the router with `{value: msg.value}`), rather than to the end user, permanently trapping the funds in `EvmHost`.

### Finding Description
When `msg.value > 0`, `dispatch(DispatchPost)` performs: [1](#0-0) 

The Uniswap V2 Router's `swapETHForExactTokens(amountOut, path, to, deadline)` computes the exact amount of ETH needed to produce `amountOut` of the output token, wraps only that amount, and refunds any leftover ETH to `msg.sender` of that call — which is `EvmHost`, not the original transaction sender (`_msgSender()`). The `to` parameter only controls where the swapped `feeToken` output goes (set to `address(this)`), not where the ETH refund goes.

`EvmHost` never captures the returned `amounts[]` from the swap call and never forwards any leftover ETH back to `_msgSender()`. Compare this to `IntentGatewayV2.sol`, which correctly does capture the swap output and refunds the difference: [2](#0-1) 

The same missing-refund pattern is repeated in `dispatch(DispatchGet)`: [3](#0-2) 

and in `fundRequest()`: [4](#0-3) 

Because a caller (an app contract dispatching a POST/GET request, or a user/relayer funding a pending request) typically does not know the exact required native amount on-chain — the documentation explicitly warns against calling `quote()` on-chain due to sandwich-attack risk and recommends only off-chain estimation with a margin — any overestimation of `msg.value` results in the excess being refunded by the router to `EvmHost` and then stranded there, since `EvmHost` has no mechanism observed to sweep or forward that ETH back to depositors. [5](#0-4) 

This mirrors the reported LayerZero bug exactly: a refund destined for the original payer is instead delivered to the intermediary contract's own balance (`Bridge.sol` in the report, `EvmHost` here) because the wrong "refund recipient" context is used, permanently locking funds.

### Impact Explanation
Any application contract or user dispatching a POST/GET request with native token payment, or funding a pending request's relayer fee, that supplies `msg.value` even slightly above the exact swap requirement (which is unavoidable in practice since on-chain slippage/price movement makes exact quoting impossible and off-chain estimation is explicitly recommended with a buffer) will have the difference permanently locked inside `EvmHost`. This affects every dispatch path across the protocol (`HyperApp.dispatchWithFeeToken`/native dispatch callers, `IntentGatewayV2` fee dispatch calls to the host, `HyperbridgeLzEndpoint.send`, `HyperFungibleToken.send`, and any third-party `IApp` contract), since they all ultimately call `IDispatcher(host).dispatch{value: msg.value}(...)`. This is a protocol-wide, permanent freezing-of-funds bug reachable by any unprivileged message dispatcher, token bridger, or relayer funding a request.

### Likelihood Explanation
High likelihood: exact native-value quoting for a fee-token swap is inherently imprecise (subject to slippage/price movement between quote and execution), and the documentation itself instructs developers to over-provision `msg.value` off-chain. Every call to `dispatch()`/`fundRequest()` with native payment that isn't perfectly exact triggers the loss, making this a routine occurrence rather than an edge case.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the `amounts` array returned by `swapETHForExactTokens` and refund `msg.value - amounts[0]` back to `_msgSender()`, following the same pattern already implemented correctly in `IntentGatewayV2._newOrder`/`placeOrder` (`evm/src/apps/IntentGatewayV2.sol` lines 383-397).

### Proof of Concept
1. An `IApp` contract calls `IDispatcher(host).dispatch{value: X}(post)` where `X` is intentionally or unavoidably larger than the exact ETH-in amount needed to produce `post.fee` of `feeToken` (e.g., due to off-chain quote buffer or slippage between quote-time and execution-time).
2. Inside `EvmHost.dispatch`, `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` is called; the Uniswap V2 router wraps only the needed ETH into WETH, swaps it for `post.fee` of `feeToken` sent to `address(this)` (the Host), and refunds `X - amounts[0]` in raw ETH to `msg.sender`, i.e., `EvmHost`.
3. `EvmHost.dispatch` does not read the `amounts` return value and does not forward any ETH back to the original caller.
4. The refunded ETH now sits in `EvmHost`'s balance with no code path shown in `EvmHost.sol` to withdraw or forward it back to depositors, permanently locking those funds.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L383-397)
```text
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
