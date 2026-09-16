Confirmed: `EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all call `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)` without capturing the returned `amounts` array and without refunding any leftover native token to `_msgSender()`. This is a direct analog of the reported bug class.

### Title
Excess native token sent to `EvmHost.dispatch()`/`fundRequest()` is not refunded to the caller and becomes permanently stuck - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` swap any native token sent via `msg.value` for the exact fee-token amount required (`post.fee` / `get.fee` / `amount`) using `swapETHForExactTokens`. Any native token beyond what the swap consumes is refunded by the Uniswap router to `msg.sender` in the router's call context — which is `EvmHost` itself, not the original transaction sender. `EvmHost` never captures this refund or forwards it back to `_msgSender()`, so any overpayment is permanently trapped in the `EvmHost` contract.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 
the code does `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp);` and discards the return value entirely. The same pattern appears in `dispatch(DispatchGet)`: [2](#0-1) 
and in `fundRequest()`: [3](#0-2) 

The standard `UniswapV2Router02.swapETHForExactTokens` implementation refunds any `msg.value` not consumed by the swap back to `msg.sender` of the router call — which, from the router's perspective, is `EvmHost`, since `EvmHost` is the one invoking the router with `{value: msg.value}`. That refund therefore lands in `EvmHost`'s own balance rather than being routed back to the original caller (`_msgSender()`). None of these three functions checks `address(this).balance` before/after the swap or forwards any residual ETH back to the caller.

This is confirmed to be a known bug class within this same codebase: the same overpayment problem was identified and explicitly fixed in `IntentGatewayV2.placeOrder()`, which does capture `amounts[0]` from the swap and refunds `msgValue - amounts[0]` back to the user: [4](#0-3) 
No equivalent refund logic exists in `EvmHost`.

### Impact Explanation
Any unprivileged user or contract dispatching a POST/GET request or funding a request with native token overpayment (which is the expected normal flow, since callers must send `msg.value >= required fee amount` and typically pad for slippage/quote imprecision, as explicitly documented: "Estimate Fees Off-Chain ... Do not call `quote()` in smart contract transactions" and "generous 2x buffer" patterns seen elsewhere in the codebase) will have the unconsumed native token permanently locked in `EvmHost`, with no withdrawal path back to them. This is a direct, concrete loss of funds for every caller who overpays via `msg.value` on these three code paths, and the amounts lost scale with usage of the core dispatch functions used across the entire protocol (all `HyperApp`s, the `HyperFungibleToken`, `IntentGatewayV2` fee-swap flow via `dispatchWithFeeToken`, etc., that route through `IDispatcher(host()).dispatch{value: msg.value}(...)`).

### Likelihood Explanation
High likelihood: overpaying `msg.value` is the expected/documented behavior since `quote()` should not be relied upon precisely on-chain (fee estimation is inherently approximate and subject to slippage/sandwiching, per the docs' own warning), and every dispatch call that uses native payment is affected. No malicious actor is required — normal usage by any well-intentioned caller triggers permanent fund loss.

### Recommendation
Capture the `amounts` return value from `swapETHForExactTokens` in all three functions (`dispatch(DispatchPost)`, `dispatch(DispatchGet)`, `fundRequest()`) and refund `msg.value - amounts[0]` back to `_msgSender()`, mirroring the refund logic already implemented in `IntentGatewayV2.placeOrder()`.

### Proof of Concept
1. A `HyperApp` calls `IDispatcher(host()).dispatch{value: msg.value}(post)` with `post.fee = 100` (fee-token units) but sends `msg.value` equivalent to significantly more native token than the current pool price requires (e.g., due to normal price movement between off-chain quote and on-chain execution, or simply padding for safety).
2. Inside `EvmHost.dispatch(DispatchPost)`, `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` executes, consuming only `amounts[0] < msg.value` native token and sending the fee token to `EvmHost`.
3. The Uniswap router refunds `msg.value - amounts[0]` to `msg.sender`, i.e., to `EvmHost` itself.
4. `EvmHost` never forwards this refund to the original caller; the difference remains stuck in `EvmHost`'s native balance indefinitely, with no recovery mechanism in `EvmHost.sol`.

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
