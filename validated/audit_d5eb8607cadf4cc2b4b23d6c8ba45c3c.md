### Title
Excess native ETH sent to `EvmHost.dispatch()`/`fundRequest()` is not refunded to the caller and becomes permanently stuck — (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept native ETH via `msg.value` and swap it for the exact fee-token amount needed using `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)`. None of these three functions check for or refund any leftover ETH to the original caller after the swap completes.

### Finding Description
In each of these functions, the entire `msg.value` is forwarded to the Uniswap V2 router: [1](#0-0) [2](#0-1) [3](#0-2) 

`UniswapV2Router02.swapETHForExactTokens` only consumes `amounts[0] <= msg.value` ETH and refunds the dust (`msg.value - amounts[0]`) to its immediate caller via `TransferHelper.safeTransferETH(msg.sender, ...)`. Since `EvmHost` itself calls the router directly (not via `delegatecall`), the router's `msg.sender` is `EvmHost`, not the original transaction sender or the calling app contract. The refunded dust ETH therefore lands in `EvmHost`'s own balance rather than being returned to the party that originally sent it.

None of the three functions read the router's returned `amounts[0]` or otherwise compute and forward back any unspent `msg.value` to `_msgSender()`/`post.payer`. Contrast this with `IntentGatewayV2` and `ExtrinsicIntents`, which explicitly track `msgValue -= amounts[0]` and call `_sendValue(msg.sender, msgValue)` to refund any excess: [4](#0-3) [5](#0-4) 

`EvmHost` lacks this same accounting/refund step despite implementing the identical "swap native ETH for exact fee-token amount" pattern.

### Impact Explanation
Any unprivileged caller — a `HyperApp` developer's contract, an SDK-generated transaction, or a user directly calling `IDispatcher(host).dispatch{value: msg.value}(...)` — who overestimates the ETH needed to cover the relayer/dispatch fee (a normal and encouraged practice, since exact quotes drift with pool price and the docs themselves recommend sending buffer amounts, e.g. the 2x buffer noted in `HyperbridgeLzEndpoint.quote`) will have the excess ETH permanently absorbed into the `EvmHost` contract balance with no code path to reclaim it. This is a direct loss of user/application funds on every over-funded native dispatch, get-request, or `fundRequest` call — the exact bug class described in the reference report (fee overestimation → un-refundable excess payment).

### Likelihood Explanation
High likelihood: `dispatch()` and `fundRequest()` are the primary, most frequently used unprivileged entry points into Hyperbridge for native-token fee payment, and both the docs and tests demonstrate over-funding as a normal usage pattern (fee estimates must include buffer for price/timing drift). Every such call that isn't penny-precise leaks value into `EvmHost`.

### Recommendation
After the `swapETHForExactTokens` call, capture the returned `amounts[0]` (actual ETH spent) and refund `msg.value - amounts[0]` back to `_msgSender()` (or `post.payer`/`get.payer` as appropriate), mirroring the pattern already used in `IntentGatewayV2._sendValue` / `ExtrinsicIntents`. Apply this fix to `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` in `EvmHost.sol`.

### Proof of Concept
1. Caller (e.g., a `HyperApp` or EOA) invokes `IDispatcher(host).dispatch{value: 5 ether}(DispatchPost{... fee: X ...})` where the actual ETH needed to acquire `X` fee-tokens via Uniswap is only `0.1 ether`.
2. Inside `EvmHost.dispatch`, `swapETHForExactTokens{value: 5 ether}(X, path, address(this), block.timestamp)` spends `0.1 ether` and refunds `4.9 ether` dust — but the refund target is `msg.sender` from the router's perspective, i.e., `EvmHost`, not the caller.
3. `EvmHost`'s ETH balance increases by `4.9 ether`; the original caller receives nothing back and has no function to reclaim it.
4. Repeat with `fundRequest` for the same effect on any call that over-funds relative to the actual swap cost.

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
