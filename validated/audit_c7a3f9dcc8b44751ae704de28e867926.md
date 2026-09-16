### Title
Unbounded-slippage native fee-token swap in `placeOrder` enables sandwich extraction of user ETH - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
When a user pays the solver fee (`order.fees`) in native ETH, `IntentGatewayV2.placeOrder` swaps the ETH for the exact fee-token amount via Uniswap V2 with no independent slippage bound and a `deadline` of `block.timestamp`, exposing the transaction to a sandwich attack that forces the user to overpay for the same `order.fees` output — the same "slippage caused by forced token exchange" bug class cited in the ParaSpace incident report.

### Finding Description
In the fee-handling branch of `placeOrder`, when `msgValue > 0` the entire remaining native value is forwarded to `swapETHForExactTokens`: [1](#0-0) 

`swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)` requests an *exact* output amount (`order.fees` in fee-token units) with the caller's whole leftover native balance (`msgValue`) acting as the only ceiling on `amountIn`. There is no separate, price-aware `amountInMax` parameter derived from an off-chain quote, and `deadline = block.timestamp` provides no protection against same-block manipulation — it only prevents the swap from executing in a later block.

Because a user's `placeOrder` call is a normal, unprivileged transaction visible in the mempool, an attacker can:
1. Front-run with a trade that moves the WETH/feeToken pool reserves against the user.
2. Let the victim's `swapETHForExactTokens` execute at the manipulated price, consuming far more ETH than the fair-market amount to obtain the same `order.fees` tokens.
3. Back-run to restore the pool and capture the price difference as profit.

The user's `msgValue` (the router's `amountInMax` in practice) absorbs the entire manipulated cost; only the unused remainder is refunded via `msgValue -= amounts[0]` and the final refund step: [2](#0-1) 

This mirrors the ParaSpace bug class where forced/implicit token exchanges without adequate slippage bounds during an attack window directly leaked value to the attacker via price manipulation, rather than via a broken invariant elsewhere in the protocol.

### Impact Explanation
Any user paying `order.fees` in native ETH is exposed to direct fund loss proportional to how far the attacker can move the WETH/feeToken pool within one block, up to the user's full remaining `msg.value`. This is a concrete theft of user funds reachable from a single, unprivileged `placeOrder` transaction — no special privileges, governance, or off-chain component compromise required.

### Likelihood Explanation
`placeOrder` is a core, frequently-used, permissionless entry point for the Intent Gateway. Any solver-fee-in-native-ETH order is vulnerable, and the pool being sandwiched is the standard Uniswap V2 WETH/feeToken pair configured via `IDispatcher(hostAddr).uniswapV2Router()` and `feeToken()`, which is realistically thin/manipulable relative to a well-funded attacker, especially on less liquid destination chains.

### Recommendation
Require the caller to supply an explicit `amountInMax` (derived from an off-chain quote with a caller-chosen slippage tolerance) instead of implicitly using the entire `msgValue`, and/or use `swapExactETHForTokens` with a real minimum-output check against a caller-supplied acceptable price, plus a genuine future `deadline` parameter passed by the caller rather than `block.timestamp`.

### Proof of Concept
1. Attacker observes a pending `placeOrder` transaction with `order.fees > 0` and `msg.value` covering the fee swap.
2. Attacker front-runs with a large WETH→feeToken (or feeToken→WETH) swap on the same Uniswap V2 pool referenced by `IDispatcher(hostAddr).uniswapV2Router()` to skew reserves.
3. Victim's transaction executes `swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)` at the skewed price, consuming a much larger `amounts[0]` of ETH than the fair-market rate for `order.fees` tokens.
4. Attacker back-runs to restore the pool, netting the ETH overpayment as profit; the victim's refunded `msgValue - amounts[0]` is correspondingly smaller than expected.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L375-392)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
