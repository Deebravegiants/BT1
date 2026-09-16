### Title
`EvmHost.dispatch()`/`fundRequest()` swap excess native ETH into the host contract instead of refunding the caller - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept `msg.value` and forward the entire amount to `swapETHForExactTokens{value: msg.value}(fee, ...)`, but never account for or return unspent native ETH to the original caller, unlike `IntentGatewayV2.sol`/`ExtrinsicIntents.sol`, which explicitly refund unspent `msgValue` back to `msg.sender` after their own fee-swap calls.

### Finding Description
`EvmHost.dispatch(DispatchPost)` swaps `msg.value` for an exact amount of fee tokens via Uniswap: [1](#0-0) . `dispatch(DispatchGet)` and `fundRequest()` follow the identical pattern [2](#0-1) [3](#0-2) .

`swapETHForExactTokens` on a standard Uniswap V2 router only consumes the ETH needed to buy the exact `amount`/`fee` output and refunds the remainder to `msg.sender` **of the router call**. Because `EvmHost` itself is the caller of the router (`IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, ...)`), any refund the router issues lands back on `EvmHost`, not on the original external caller who supplied the `msg.value` to `dispatch()`/`fundRequest()`. `EvmHost` never reads a return value from the swap, never computes `msg.value - amountSpent`, and never forwards any leftover ETH back to `_msgSender()`.

Contrast this with the sibling app contracts, which do correctly implement a refund pattern for the exact same swap call: `IntentGatewayV2.sol` computes `msgValue -= amounts[0]` and then calls `_sendValue(msg.sender, msgValue)` for any leftover [4](#0-3) , and `ExtrinsicIntents.sol` does the same for solver overpayment [5](#0-4) . `EvmHost.sol` lacks this logic entirely.

`EvmHost` has no `receive()`/`fallback()` and no user-facing sweep function for stray native ETH; the only native-ETH exit path is `withdraw()`, gated to the cross-chain governance-controlled `hostManager` [6](#0-5) . Excess ETH accumulated this way is therefore not recoverable by the caller who overpaid — it can only ever be swept by governance to an arbitrary beneficiary, never back to the original overpayer.

### Impact Explanation
Any unprivileged contract or EOA calling `IDispatcher(host).dispatch{value: msg.value}(post)` (or the GET variant, or `fundRequest`) with `msg.value` greater than what the Uniswap pool needs to fill the exact `fee`/`amount` will have the excess permanently stuck in `EvmHost`, non-recoverable by that caller. This is a realistic scenario: documentation explicitly instructs integrators to "send enough native tokens to cover fees" and quote fees client-side beforehand (`docs/content/developers/evm/messaging/post-requests.mdx`), meaning any over-estimation, price movement between quote and execution, or deliberately generous buffer (as the SDK's own `HyperbridgeLzEndpoint.quote()` applies a 2x buffer "Excess native is refunded by the uniswap router") results in a permanent loss of user funds. This qualifies as permanent freezing/loss of user funds reachable from a single unprivileged `dispatch`/`fundRequest` transaction.

### Likelihood Explanation
High likelihood: every POST/GET dispatch or fee top-up paid in native token goes through this exact code path, and precise fee estimation is inherently probabilistic given AMM slippage and time between quoting and execution. The bug requires no attacker and no special conditions — it triggers on ordinary use whenever the caller's `msg.value` exceeds the router's exact-output requirement.

### Recommendation
After each `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the `amounts` return value, compute `msg.value - amounts[0]`, and forward any surplus back to `_msgSender()` (mirroring the pattern already used in `IntentGatewayV2.sol` and `ExtrinsicIntents.sol`).

### Proof of Concept
1. Caller calls `IDispatcher(host).dispatch{value: 1 ether}(DispatchPost{..., fee: X})` where the current Uniswap pool price only requires `0.1 ether` to buy `X` fee tokens.
2. `EvmHost.dispatch` executes `swapETHForExactTokens{value: 1 ether}(X, path, address(this), block.timestamp)`.
3. The router spends `0.1 ether`, refunds `0.9 ether` to `msg.sender` of the router call, which is `EvmHost` (not the caller).
4. `EvmHost.dispatch` returns without touching the leftover `0.9 ether`; it now sits in `EvmHost`'s balance.
5. The caller has no function to reclaim the `0.9 ether`; only cross-chain governance via `HostManager`/`withdraw()` can move it, and only to a governance-chosen beneficiary — never automatically back to the original caller.

### Citations

**File:** evm/src/core/EvmHost.sol (L647-660)
```text
    /**
     * @dev withdraws host revenue to the given address, can only be called by cross-chain governance
     * @param params, the parameters for withdrawal
     */
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
