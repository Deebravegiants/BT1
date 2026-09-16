### Title
Native-fee-to-feeToken swap via `uniswapV2Router` can permanently block message dispatch and order placement paths - ([File: evm/src/core/EvmHost.sol], [File: evm/src/apps/IntentGatewayV2.sol])

### Summary
Both `EvmHost.fundRequest()` and `IntentGatewayV2.placeOrder()` assume that a fixed, per-chain `uniswapV2Router` configured on the host is a fully functional Uniswap V2 deployment with a liquid `WETH/feeToken` pair, and unconditionally call `swapETHForExactTokens` on it whenever a caller pays with native tokens instead of the fee token directly.

### Finding Description
`IDispatcher(hostAddr).uniswapV2Router()` is read and invoked directly in `IntentGatewayV2.placeOrder()`: [1](#0-0) 

and identically in the Tron fork of `IntentGatewayV2.sol`: [2](#0-1) 

The same pattern exists at the core `EvmHost.fundRequest()`, used to top up relayer fees for undelivered requests: [3](#0-2) 

In every case, the code hard-codes the assumption that a "local uniswap router" exists on the chain and that a `WETH -> feeToken` path resolves to a working liquidity pool. This exactly mirrors the reported bug class: an external, chain-specific protocol dependency (Synthetix's wrapper contract on OP vs Ethereum) that is silently non-functional or incompatible on some deployments, causing calls that depend on it (`mint()` there, `swapETHForExactTokens` here) to revert unconditionally. On many EVM chains where Hyperbridge is deployed, no canonical (or liquid) Uniswap V2 fork may exist for the configured fee token, or the configured router address may point to a router with no pool for that pair — the swap then always reverts.

### Impact Explanation
Any unprivileged user who tries to pay a solver/relayer fee in native token (rather than pre-approved fee token) on a chain where the configured `uniswapV2Router` lacks a `WETH/feeToken` pool will have their `placeOrder` transaction revert every time. Since this is the code path explicitly documented as the fallback for native-token fee payment ("The placement transaction carries nativeValue extra wei, which the gateway swaps into the fee token through its configured router"), this makes the native-fee path for placing orders — or for topping up relayer fees via `fundRequest` — completely non-functional on any chain where this dependency assumption doesn't hold, without any other route to recover: the ISMP message or intent order simply cannot be placed/funded through this path, and no fallback contract call exists to keep the flow going as intended by the protocol design. This matches "a route unable to deliver messages" for a subset of chains and users.

### Likelihood Explanation
Likelihood is real but limited: the failure mode requires the deployment/governance to have configured a chain's `uniswapV2Router` incorrectly (e.g. an inactive fork, or a router with a genuinely illiquid feeToken pair) — a scenario that is entirely plausible given how many EVM-compatible chains Hyperbridge targets, none of which are guaranteed to have deep UniswapV2 liquidity for Hyperbridge's arbitrary fee token, exactly as OP Chain's Synthetix wrapper differed silently from Ethereum's. Because a working fee-token-direct path (ERC20 approval + `safeTransferFrom`) always exists as an alternative when `msgValue == 0`, this is a availability/DoS issue for one payment mode rather than a fund-freezing bug — funds are never escrowed if the swap reverts (the `placeOrder`/`fundRequest` call is atomic and rolls back entirely).

### Recommendation
Do not hard revert the entire dispatch/order-placement flow when the native-token swap fails. Options:
- Validate `uniswapV2Router` liquidity/pool existence during governance configuration (e.g. require `getAmountsOut` to return a sane, non-zero quote) before allowing the router to be set live for a chain.
- Wrap the `swapETHForExactTokens` call in a try/catch and fall back to reverting with a clear, specific error (`NativeFeeSwapUnavailable`) so callers can retry using the ERC20 fee-token path instead of a generic router-call revert, and document per-chain whether native-fee payment is supported.
- Consider supporting multiple DEX adapters or a configurable swap router interface per chain instead of assuming one canonical UniswapV2 deployment across all supported EVM chains.

### Proof of Concept
Not applicable as a live exploit — this is a configuration/dependency-availability issue, analogous to the source report. To reproduce conceptually: deploy `EvmHost`/`IntentGatewayV2` on a chain, configure `uniswapV2Router` to a real UniswapV2Router02 contract that has no `WETH/feeToken` pool (or a zero-liquidity pool), then call `placeOrder` with `order.fees > 0` and `msg.value > 0`. `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)` reverts (as seen at [4](#0-3) ), causing the whole `placeOrder` transaction to revert and blocking that fee-payment method entirely for that chain.

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

**File:** evm/src/core/EvmHost.sol (L1021-1043)
```text
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * If called on an already delivered request, these funds will be seen as a donation to the hyperbridge protocol.
     * @param commitment - The request commitment
     * @param amount - The amount provided in `feeToken()`
     */
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
