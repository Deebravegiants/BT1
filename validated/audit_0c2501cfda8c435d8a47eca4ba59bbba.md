### Title
Excess native-token payment in `EvmHost.dispatch()` / `fundRequest()` is not refunded and can become permanently stuck - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` accept native ETH via `msg.value` and swap it for the exact `feeToken` amount needed (`post.fee` / `get.fee`) using `swapETHForExactTokens{value: msg.value}(...)`, but never account for or refund any leftover native value to the original caller. Any relayer, message dispatcher, or application forwarding user-supplied `msg.value` that exceeds what's required for the Uniswap swap risks losing the difference, unless the router itself refunds excess ETH to the immediate caller.

### Finding Description
In `dispatch(DispatchPost memory post)`: [1](#0-0) 
the full `msg.value` is forwarded to `swapETHForExactTokens`, but the function never captures unspent ETH nor refunds it back to `_msgSender()`. The same pattern repeats in `dispatch(DispatchGet memory get)`: [2](#0-1) 

This is materially different from the pattern that the codebase itself uses elsewhere to handle the identical situation correctly: `IntentGatewayV2.placeOrder()` captures the router's returned `amounts[0]` (actual ETH spent) and explicitly refunds the difference to `msg.sender`: [3](#0-2) 

`EvmHost.dispatch()` has no equivalent `msgValue -= amounts[0]` / `_sendValue(...)` step. Whether the excess ETH is recoverable depends entirely on whether the configured Uniswap V2 router refunds unspent ETH to `msg.sender` of the swap call — which in this call chain is `EvmHost` itself, not the original external caller. If the router refunds to `address(this)` (EvmHost), the ETH becomes stuck inside the Host contract with no code path to return it to the payer, since `EvmHost` has no rescue/refund mechanism for accidental native balance and the value was never tracked as belonging to any particular sender.

The same issue affects `fundRequest()`, which follows the identical swap pattern for increasing relayer fees on already-dispatched requests. Any caller who over-estimates the native amount needed (a very likely occurrence, given the docs explicitly warn that `quote()` is only an off-chain estimate subject to slippage) permanently overpays with no recovery mechanism.

### Impact Explanation
Any external account calling `dispatch()`/`fundRequest()` with native token payment and providing more ETH than the exact swap requirement (which is expected/common given AMM price slippage and the documented "approximate, subject to slippage" fee model) loses the excess ETH. Because the entrypoint is unauthenticated and reachable by any relayer, application, or user paying dispatch fees in native token — this is a High severity, direct value-loss vulnerability on the exact analog described in the reference report (overpayment with no refund mechanism).

### Likelihood Explanation
Likelihood is high: the documentation explicitly instructs frontends to only "estimate" the native cost off-chain via `quote()` because slippage makes the estimate imprecise, meaning users are expected, by design, to routinely send more ETH than exactly required. Every dispatch call paid in native token is exposed.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2.placeOrder`/`fillOrder`: capture the `amounts[0]` returned by `swapETHForExactTokens` in `EvmHost.dispatch()`, `dispatch(DispatchGet)`, and `fundRequest()`, compute `msg.value - amounts[0]`, and refund the difference back to `_msgSender()` via a low-level call, reverting on failure.

### Proof of Concept
1. Caller invokes `EvmHost.dispatch{value: 5 ether}(DispatchPost{... fee: 1 * 1e18 ...})` where the actual ETH needed to acquire `1e18` fee tokens via Uniswap is only `0.1 ether`.
2. `dispatch()` executes `swapETHForExactTokens{value: 5 ether}(1e18, path, address(this), block.timestamp)`.
3. The swap consumes only `0.1 ether`; the remaining `4.9 ether` is refunded by the router to `msg.sender` of the swap call, which is `EvmHost` (`address(this)`), not the original caller.
4. `EvmHost` never tracks or forwards this leftover ETH to the original caller; it accumulates in the Host contract balance with no withdrawal path tied to the payer.
5. Compare with `evm/src/apps/IntentGatewayV2.sol:383-397`, which performs the identical swap but correctly computes and refunds the unspent native amount to `msg.sender` — confirming `EvmHost.dispatch()` is missing this step.

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
