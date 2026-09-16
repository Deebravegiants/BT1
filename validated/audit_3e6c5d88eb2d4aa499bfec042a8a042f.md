### Title
Excess `msg.value` swapped via `swapETHForExactTokens` is stranded in `EvmHost` and never refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token payment and forward the entire `msg.value` to `swapETHForExactTokens`, requesting only the exact `feeToken` amount needed (`post.fee`, `get.fee`, or `amount`). Any ETH sent above what the swap actually consumes is refunded by the Uniswap router — but to `EvmHost` itself (the caller of the router), not to the original transaction sender. `EvmHost` never forwards that leftover ETH back out, so it becomes permanently stuck in the contract's balance.

### Finding Description
In `dispatch(DispatchPost memory post)`: [1](#0-0) 
the full `msg.value` is passed to `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. Uniswap V2's `swapETHForExactTokens` only consumes the ETH required to produce exactly `post.fee` output tokens and refunds any surplus ETH to `msg.sender` of that call — which is `EvmHost`, not the EOA/contract that called `dispatch`. The function then proceeds without checking or returning any leftover value.

The same pattern repeats in `dispatch(DispatchGet memory get)`: [2](#0-1) 
and in `fundRequest`: [3](#0-2) 

In all three functions, if a caller supplies `msg.value` greater than what the current pool price requires to obtain the exact `fee` amount of `feeToken`, the surplus ETH is captured by the router refund into `EvmHost`'s own balance rather than being returned to the actual payer. `EvmHost` exposes no `receive()`/`withdraw` path that returns this stranded ETH to the original sender — it simply accumulates in the contract with no accounting of who is owed it.

This is architecturally the same bug class as the referenced report: the contract validates only a lower bound implicitly (the router will revert if `msg.value` is insufficient) but never enforces or refunds the exact amount, so any overpayment above the required native amount is irrecoverably lost by the caller. Compare this to `IntentGatewayV2.placeOrder`, which explicitly tracks `msgValue` after the swap and refunds any remainder to `msg.sender`: [4](#0-3) 
`EvmHost.dispatch`/`fundRequest` have no equivalent refund step.

### Impact Explanation
Overpaying `msg.value` on `dispatch()` or `fundRequest()` is an easy, realistic user mistake — quoted fee amounts can shift between quote-time and execution-time due to Uniswap price movement, or a naive integrator may pass a generous `msg.value` "buffer" expecting excess to be refunded (as it is in `IntentGatewayV2`). Any ETH sent above the exact swap requirement is permanently locked in `EvmHost`, unrecoverable by the user, and not even recoverable by protocol governance since there is no withdrawal mechanism for stray native balance. This is a direct, permanent loss of user funds.

### Likelihood Explanation
Likelihood is low-to-moderate: it requires a caller to send more native token than the router needs to produce the requested `feeToken` amount, which can happen from stale fee quotes, deliberate "safety margin" overpayment (a common integration pattern, as documented for `IntentGatewayV2`), or gas-price/AMM-price fluctuations between quoting and submission. Because `dispatch()` and `fundRequest()` are the primary entry points for any app or user paying with native token, this is broadly reachable by any unprivileged dispatcher.

### Recommendation
After each `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, compute the leftover native balance actually consumed (mirroring `IntentGatewayV2`'s `msgValue -= amounts[0]` pattern) and refund any unspent `msg.value` back to `_msgSender()` via a low-level call, rather than leaving the router's refund stranded in `EvmHost`.

### Proof of Concept
1. Caller quotes `post.fee = 100` feeToken units and estimates it needs `1 ETH` based on current pool price, then calls `dispatch{value: 1 ETH}(post)`.
2. Before the transaction confirms, the ETH/feeToken pool price moves favorably (or the caller simply overestimates), so `swapETHForExactTokens` only needs `0.6 ETH` to produce the 100 feeToken units.
3. Uniswap's router refunds `0.4 ETH` to `msg.sender` of the swap call, i.e., `EvmHost`.
4. `EvmHost.dispatch` returns normally; the `0.4 ETH` remains in `EvmHost`'s balance with no record of ownership and no way for the original caller to reclaim it — permanently lost. Repeating this across many callers/transactions accumulates stranded, unrecoverable ETH in `EvmHost`.

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
