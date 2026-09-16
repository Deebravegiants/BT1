### Title
`IntentGatewayV2.placeOrder` uses `swapETHForExactTokens` at live Uniswap V2 spot price with no slippage bound — ([File: evm/src/apps/IntentGatewayV2.sol], mirrored in [File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
When a user places an order with `order.fees > 0` and pays in native token, `placeOrder` converts the native `msgValue` remainder into `feeToken` via `IUniswapV2Router02.swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)` [1](#0-0) . This is functionally the same bug class as the referenced `CrvDepositorWrapper` finding: an on-chain, unprotected AMM price read is used to size a critical financial operation (fee escrow) that a single submitted transaction can trigger and that an attacker can move against the user via sandwiching.

### Finding Description
`swapETHForExactTokens` requests an exact `order.fees` output of `feeToken` in exchange for up to `msgValue` of native ETH, at whatever the current pool reserves dictate [2](#0-1) . There is no independent price reference (no Chainlink oracle, no minimum/maximum bound computed off a TWAP, no caller-supplied slippage parameter) — the "price" is whatever the Uniswap V2 pool's instantaneous reserves say at execution time, exactly like the 20/80 WETH/BAL pool relied on by `CrvDepositorWrapper`. If the router or `feeToken` pool has thin liquidity (a realistic condition for a project-specific `feeToken`/WETH pair, analogous to the low-volume BAL/WETH pool in the original report), an attacker can:
1. Front-run the `placeOrder` call, moving the pool price so that acquiring `order.fees` of `feeToken` consumes far more ETH than expected, potentially exceeding `msgValue` and reverting the whole order (denial of service on order placement) — or, if `msgValue` was sized generously, consuming the user's excess ETH and leaving less refunded than expected, since `swapETHForExactTokens` refunds only the ETH not spent, and the "not spent" amount is exactly what the attacker manipulated to be worse.
2. Back-run to restore the pool, capturing the difference — a classic sandwich, identical in mechanism to the vulnerability described for `CrvDepositorWrapper`, which likewise had no minOut/oracle protection against a thin, infrequently-updated market.

This differs from the documented, deliberately off-chain-only `quote()`/`getAmountsIn()` helper (which the docs explicitly warn must not be called on-chain because it is sandwichable) [3](#0-2) : here the same class of unprotected AMM price dependency is embedded directly in the state-changing `placeOrder` path, reachable by any unprivileged user submitting an order with native-fee payment.

By contrast, `SimplexPaymaster.swapAndDeposit` was already hardened against this exact bug class: it derives `amountOutMin` from Chainlink oracles with staleness bounds (`maxOracleAge`) and a governance-capped `swapSlippageBps`, rather than trusting the AMM spot price alone [4](#0-3) , confirming the codebase is aware of and has fixed this pattern elsewhere but not in `IntentGatewayV2.placeOrder`'s fee-swap path.

### Impact Explanation
Funds impact: users paying order fees in native token can have their transaction revert (funds not lost but DoS on intent placement) or, in adverse liquidity/attack conditions, receive a worse execution than the fee amount implies, effectively overpaying ETH relative to fair value with the difference captured by a sandwiching MEV actor. Because `order.fees` is a fixed target output and the loss is borne on the input (native ETH) side without any explicit `amountInMax`/oracle check, this is a direct value-extraction vector reachable from a single unprivileged `placeOrder` call — matching the required "unprivileged message dispatcher ... reachable" criteria (IntentGatewayV2 dispatch/escrow path).

### Likelihood Explanation
Likelihood is Medium: it requires (a) a `feeToken`/WETH Uniswap V2 pool with limited liquidity relative to attacker capital, and (b) a user submitting a native-fee order, both realistic given `feeToken` is typically a protocol-specific stablecoin with a smaller pool than majors. MEV searchers routinely scan mempools for `swapETHForExactTokens`/`swapExactETHForTokens` calls lacking slippage protection, making exploitation straightforward once a suitable pool is identified.

### Recommendation
- Require callers (or compute on-chain from a Chainlink oracle, as done in `SimplexPaymaster`) to supply a bounded `maxNativeIn` for the fee swap, and revert if the actual amount spent exceeds a governance-configured slippage tolerance over an oracle-derived fair price rather than trusting the router's own reserves.
- Alternatively, disallow native-token fee payment when `order.fees > 0` and require pre-approved `feeToken`, eliminating the on-chain AMM dependency entirely (mirroring the "Fee Token Payment (Recommended)" guidance already documented for `HyperApp.dispatchWithFeeToken`).
- If native-fee swapping must remain, add a minimum received / maximum spent bound with a small deadline and consider routing through a TWAP-based or Chainlink-anchored quote similar to `SimplexPaymaster._getOraclePrice`.

### Proof of Concept
1. Deploy/observe a `feeToken`/WETH Uniswap V2 pool with modest liquidity (as configured via `IDispatcher(hostAddr).uniswapV2Router()`).
2. Attacker monitors mempool for a `placeOrder` call with `order.fees > 0` and native `msg.value`.
3. Attacker front-runs with a large swap that skews the WETH/feeToken pool price against the pending order.
4. The pending `placeOrder` executes `swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)` [5](#0-4)  at the skewed price — either reverting (if `msgValue` insufficient at the new price) or consuming far more of the user's ETH than expected to hit the exact `order.fees` output.
5. Attacker back-runs to restore the pool and pockets the price difference, having extracted value from the user's fee-swap with no on-chain protection in place.

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```

**File:** evm/src/utils/SimplexPaymaster.sol (L464-475)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;

        address[] memory path = new address[](2);
        path[0] = token;
        path[1] = IUniswapV2Router02(router).WETH();

        IERC20(token).forceApprove(router, amountIn);
        uint256[] memory amounts = IUniswapV2Router02(router)
            .swapExactTokensForETH(amountIn, amountOutMin, path, address(this), block.timestamp);
```
