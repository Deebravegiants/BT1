### Title
Native token overpayment in `EvmHost.dispatch`/`fundRequest` is never refunded, permanently trapping user funds - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all forward the entire `msg.value` into `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)` without ever comparing the actual amount consumed to what was sent, and without forwarding any leftover ETH back to the original caller.

### Finding Description
When a caller pays the Hyperbridge dispatch fee with native tokens, `EvmHost` swaps that native value for the exact `feeToken` amount needed via the local Uniswap router: [1](#0-0) [2](#0-1) [3](#0-2) 

`UniswapV2Router02.swapETHForExactTokens` is a standard router function that only consumes `amounts[0] <= msg.value` and refunds the unspent "dust" ETH to whoever called it — in this case, `EvmHost` itself (since `EvmHost` is the direct caller of the router, `msg.sender` inside the router call is the `EvmHost` contract, not the original transaction sender). None of the three `EvmHost` functions capture the router's return value, compute the unspent remainder, or send it back to `_msgSender()` / `post.payer`. The excess native tokens therefore land in `EvmHost`'s own balance with no code path to return them to the user who overpaid.

This directly parallels the reported `ExchangeProxy.executeSwapDirect` bug class, where an inequality check (`msg.value >= ethValue`) accepts overpayment but the excess is not routed back to the sender. The rest of the Hyperbridge codebase (`IntentGatewayV2.placeOrder`/`fillOrder`, `ExtrinsicIntents._fillCrossChain`, `WrappedHyperFungibleTokenUpgradeable.send`) explicitly tracks the swap's actual cost and calls `_sendValue(msg.sender, msgValue)` to refund the difference: [4](#0-3) 

`EvmHost` has no equivalent refund logic for its `dispatch`/`fundRequest` entry points, nor does it expose a general mechanism for users to reclaim stray native ETH sent through these calls.

### Impact Explanation
Any unprivileged app or EOA that dispatches a POST/GET request or funds an existing request via native token payment and sends more ETH than the exact quoted fee requires (a very likely scenario, since `quote()` is explicitly documented as an off-chain-only, sandwichable estimate subject to price movement between estimation and execution) will have the excess permanently stuck in `EvmHost`. There is no code path shown to return this value to the payer; it silently accumulates as un-refundable dust in the host contract, which is a concrete instance of a user's transferred funds becoming permanently inaccessible to them — a freezing-of-funds condition reachable from a single, ordinary dispatch transaction.

### Likelihood Explanation
High likelihood in practice: since the docs explicitly warn against calling `quote()` on-chain and recommend off-chain estimation, and native fee token prices fluctuate via Uniswap, users/integrators routinely pad `msg.value` above the exact quote to avoid reverts (`Will revert if enough native tokens are not provided`). Every such overpayment is silently absorbed rather than refunded, so the bug triggers under normal usage patterns, not just adversarial ones.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the `amounts` array returned by `swapETHForExactTokens`, compute `msg.value - amounts[0]`, and refund the difference to `_msgSender()` (or the designated payer), following the same pattern already used in `IntentGatewayV2`/`ExtrinsicIntents`/`WrappedHyperFungibleTokenUpgradeable`.

### Proof of Concept
1. Caller invokes `EvmHost.dispatch{value: X}(post)` where `X` intentionally exceeds the ETH amount needed to obtain `post.fee` feeTokens from the Uniswap pool (e.g., due to price drift after off-chain quoting, or intentional padding for safety margin).
2. Inside `dispatch`, `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` executes; the Uniswap router spends `amounts[0] < X` and refunds `X - amounts[0]` ETH back to `msg.sender` of that call, which is `EvmHost`.
3. `EvmHost.dispatch` never reads `amounts[0]`, never computes the remainder, and never forwards it back to the caller; the request is dispatched and the function returns normally.
4. The refunded dust (`X - amounts[0]`) remains permanently in `EvmHost`'s native balance, unreachable by the original caller through any exposed function in the reviewed code.

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
