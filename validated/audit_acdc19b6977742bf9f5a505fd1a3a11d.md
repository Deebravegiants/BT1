### Title
`IntentGatewayV2.placeOrder` swaps native token for `feeToken` via Uniswap V2 without handling the case where `feeToken` equals `WETH`, causing a revert - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
When a user places an order with `order.fees > 0` and pays the dispatch fee in native ETH (`msgValue > 0`), `placeOrder` unconditionally builds a Uniswap V2 path `[WETH, feeToken]` and calls `swapETHForExactTokens`. This mirrors the `USSDRebalancer.BuyUSSSellCollateral` bug class: a branch that assumes the two assets on either side of a swap are always distinct, without an explicit check/short-circuit for the case where they coincide (there, collateral == DAI/base asset; here, `feeToken` == `WETH`).

### Finding Description
`placeOrder` escrows the order's input tokens and, if the order specifies non-zero `order.fees`, collects the protocol fee token from the caller: [1](#0-0) 

```solidity
if (order.fees > 0) {
    // escrow fees
    address feeToken = IDispatcher(hostAddr).feeToken();
    if (msgValue > 0) {
        address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
        address WETH = IUniswapV2Router02(uniswapV2).WETH();
        address[] memory path = new address[](2);
        path[0] = WETH;
        path[1] = IDispatcher(hostAddr).feeToken();
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
            order.fees, path, address(this), block.timestamp
        );
    } else {
        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
    }
    _orders[commitment][TRANSACTION_FEES] = order.fees;
}
```

The identical pattern exists in the non-tron `evm/src/apps/IntentGatewayV2.sol` gateway (same fee-collection logic is reused by `placeOrder`).

The code branches on whether native value was supplied (`msgValue > 0` vs. else), exactly like the reported `USSDRebalancer` bug branches on whether the collateral needs a swap at all. But it does **not** branch on whether `feeToken == WETH` (the "no swap needed" case analogous to DAI == collateral). Uniswap V2's router/pair-derivation logic reverts with `IDENTICAL_ADDRESSES` (or equivalent) when `path[0] == path[1]`, because `UniswapV2Library.sortTokens`/`pairFor` requires distinct token addresses. If Hyperbridge's configured `feeToken()` is ever the chain's wrapped-native asset (WETH/WBNB/etc.) — which is an operationally normal configuration choice for host params, just as DAI is a normal collateral for USSD — any `placeOrder` call that pays the fee in native ETH will always revert, because the swap path degenerates to `[WETH, WETH]`.

### Impact Explanation
This blocks the entire "pay dispatch fee in native token" path of the Intents order-placement flow whenever the fee token is configured to be the wrapped native asset. Since `placeOrder` is the sole unprivileged entry point for creating cross-chain/same-chain intents and dispatching them into Hyperbridge, this is a denial-of-service on order creation for any caller using `msg.value` to cover `order.fees` — a legitimate, commonly used code path (it's the reason the branch exists at all). This is a "route unable to deliver messages" style failure at the intents layer: users cannot fund their order fee via native ETH under that host configuration, forcing them either to hold and pre-approve the exact fee token or lose the ability to place orders through that gateway instance at all. It does not directly enable fund theft, but it is a High-severity availability break in message dispatch analogous to the original finding (USSD rebalancer being unable to rebalance).

### Likelihood Explanation
Likelihood depends entirely on host/deployment configuration: whether `IDispatcher(host).feeToken()` is ever set to the chain's WETH/wrapped-native address. Hyperbridge hosts already special-case the native-vs-fee-token relationship elsewhere (e.g. `EvmHost.fundRequest` swaps `WETH -> feeToken`, `GnosisUniswapV2Wrapper` special-cases a chain whose native asset is its stablecoin), showing that "fee token equals (or is derived from) the native/wrapped asset" is a realistic configuration this codebase already anticipates in other call sites. Any deployment/governance choice that sets `feeToken()` to WETH (e.g., to simplify fee accounting on a chain) immediately triggers this revert for every native-funded `placeOrder` fee payment — a single unprivileged transaction is enough to demonstrate it, and no attacker action beyond calling `placeOrder{value: ...}` is required.

### Recommendation
Before building the swap path, check whether `feeToken == WETH` (or more generally whether the native asset already collected can satisfy `order.fees` directly) and skip the Uniswap V2 swap in that case, mirroring the fix recommended for `USSDRebalancer`:

```solidity
if (order.fees > 0) {
    address feeToken = IDispatcher(hostAddr).feeToken();
    if (msgValue > 0) {
        address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
        address WETH = IUniswapV2Router02(uniswapV2).WETH();
        if (feeToken == WETH) {
            // No swap needed: wrap the exact fee amount directly.
            IWETH(WETH).deposit{value: order.fees}();
            if (msgValue > order.fees) {
                (bool sent,) = msg.sender.call{value: msgValue - order.fees}("");
                if (!sent) revert InsufficientNativeToken();
            }
        } else {
            address[] memory path = new address[](2);
            path[0] = WETH;
            path[1] = feeToken;
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                order.fees, path, address(this), block.timestamp
            );
        }
    } else {
        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
    }
    _orders[commitment][TRANSACTION_FEES] = order.fees;
}
```

### Proof of Concept
1. Deploy/configure a Hyperbridge `EvmHost` such that `feeToken()` returns the chain's canonical WETH address (a valid, non-malicious host configuration; the codebase already treats WETH/native specially elsewhere).
2. Any user calls `IntentGatewayV2.placeOrder{value: fee + inputs}(order, graffiti)` with `order.fees > 0` and enough `msg.value` to cover both the native input asset (if any) and the dispatch fee.
3. Inside `placeOrder`, `msgValue > 0` after covering inputs, so the code builds `path = [WETH, feeToken] = [WETH, WETH]` and calls `IUniswapV2Router02.swapETHForExactTokens`.
4. The Uniswap V2 router reverts (`IDENTICAL_ADDRESSES`/library revert) because the path's two tokens are identical, and the entire `placeOrder` transaction reverts — the order can never be placed while paying the fee in native ETH under this configuration.

*(Note: I could not fully confirm from the indexed code whether any current mainnet deployment actually sets `feeToken()` to WETH — that configuration detail lives in deployment/governance data not present in the indexed contract state. The vulnerability is in the contract logic itself: it lacks the defensive branch regardless of current configuration, exactly as the original `USSDRebalancer` report describes a logic gap rather than a currently-triggered state.)*

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-488)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```
