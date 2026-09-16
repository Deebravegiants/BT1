### Title
EvmHost.dispatch/fundRequest send Uniswap's ETH refund to the wrong address, permanently stranding user overpayment - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all let a caller pay the relayer fee in native token by forwarding the entire `msg.value` to `swapETHForExactTokens`, but they discard the function's return value and never refund any unspent ETH back to the original caller (`_msgSender()`). Because the Uniswap V2 router refunds unused ETH to its immediate caller (`EvmHost`, i.e. `address(this)`), any overpayment is captured by the Host contract itself instead of being returned to the user, mirroring the reported HardenedTopupProxy/ExchangeProxy "change not sent to sender" bug class.

### Finding Description
`dispatch(DispatchPost)`: [1](#0-0) 

`dispatch(DispatchGet)`: [2](#0-1) 

`fundRequest`: [3](#0-2) 

In each of these functions, when `msg.value > 0` the whole `msg.value` is forwarded to `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee/amount, path, address(this), block.timestamp)`. This mirrors exactly the pattern in the external report, where `ExchangeProxy` swaps the caller's full native-token balance for an exact output amount and any leftover is not returned to the original sender. Uniswap V2's canonical `swapETHForExactTokens` implementation refunds `msg.value - amounts[0]` to `msg.sender` of that call — which here is `EvmHost` itself (since `EvmHost` is the one invoking the router), not the account that sent the transaction to `EvmHost` (`_msgSender()`). The dispatch functions never capture the swap's return value (`amounts[0]`) and never compute or forward a refund to the true payer.

This is directly analogous to the reported bug in `HardenedTopupProxy`/`ExchangeProxy`, where `msg.value - ethValue` is silently retained by the contract instead of returned to the user. Notably, the codebase's own `IntentGatewayV2.sol` fixed this exact class of issue by capturing the swap's return value and refunding the delta to `msg.sender`: [4](#0-3) 
but the same pattern was never applied to `EvmHost`'s `dispatch`/`fundRequest` functions, which are the base-layer, unprivileged, most commonly used entry points for a user or app contract dispatching an ISMP message with native-token fee payment.

### Impact Explanation
Any account calling `EvmHost.dispatch()` or `EvmHost.fundRequest()` with `msg.value` greater than the exact ETH needed to acquire `post.fee`/`get.fee`/`amount` worth of `feeToken` loses the difference permanently — the excess ETH accumulates in the `EvmHost` contract balance with no code path visible in `dispatch`/`fundRequest` to return it to the payer. This is a direct, unprivileged loss of user funds reachable from a single transaction (any POST/GET dispatch or fee top-up paid in native token), matching the "concrete theft or permanent freezing of funds" bar. Given that `dispatch()` is the primary entry point used across the protocol (HyperApp helpers, HyperFungibleToken, IntentGateway's own cross-chain post, etc.) whenever apps forward `msg.value` for native fee payment, and fee estimation off-chain (`quote()`) is inherently approximate/front-runnable per the docs, overpayment is a realistic, common occurrence, not an edge case.

### Likelihood Explanation
High likelihood: the docs explicitly instruct integrators to estimate the native fee off-chain via `quote()` and warn that this is vulnerable to sandwich attacks, meaning discrepancies between the quoted/sent `msg.value` and the amount actually consumed by the swap are expected and routine. Every caller using the native-token payment path — end users calling through a HyperApp wrapper or app contracts forwarding `msg.value` — is exposed each time they pay fees with native tokens instead of fee tokens.

### Recommendation
Capture the return value of `swapETHForExactTokens` (`amounts[0]`) in all three functions (`dispatch(DispatchPost)`, `dispatch(DispatchGet)`, `fundRequest`) and refund `msg.value - amounts[0]` to `_msgSender()` (or the designated payer) after the swap, following the same pattern already implemented in `IntentGatewayV2.sol`'s `_placeOrder`/order-fee logic.

### Proof of Concept
1. Caller A calls `EvmHost.dispatch(DispatchPost)` with `post.fee = 100e18` (feeToken units) and sends `msg.value = 1 ether`, while the actual ETH needed to buy `100e18` feeToken via the configured Uniswap V2 pool is only `0.1 ether`.
2. Inside `dispatch`, `swapETHForExactTokens{value: 1 ether}(100e18, [WETH, feeToken], address(this), block.timestamp)` is called; the router consumes `0.1 ether` and refunds the remaining `0.9 ether` — but the refund target is `msg.sender` of that call, i.e. `EvmHost`.
3. `EvmHost`'s ETH balance increases by `0.9 ether`; `dispatch` never reads the swap's return value nor sends anything back to Caller A.
4. Caller A's transaction succeeds, the POST request is dispatched normally, but Caller A has permanently lost `0.9 ether` with no function in `EvmHost` shown to return it to them. [1](#0-0)

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
