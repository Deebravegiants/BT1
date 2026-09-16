## Analysis

The exploit pattern in the report is a classic AMM sandwich: a function reachable by an unprivileged actor executes a token swap through a live Uniswap-family pool without the caller being able to bound the execution price, so an attacker manipulates the pool immediately before/after the victim's swap and extracts the difference.

Hyperbridge's `EvmHost` reproduces this exact pattern in its fee-payment path. `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` all let *any* caller pay Hyperbridge's relayer fee in native token, and the Host silently swaps that native token to `feeToken()` through `IHostParams.uniswapV2` with `swapETHForExactTokens`, bounding the input only by `msg.value` — there is no caller-supplied `amountInMax`/slippage parameter distinct from `msg.value` itself, and `msg.value` is normally computed off-chain via `HyperApp.quote()`, which the docs themselves warn is "vulnerable to sandwich attacks" and should never be trusted on-chain. [1](#0-0) [2](#0-1) [3](#0-2) 

The same pattern is duplicated verbatim in `IntentGatewayV2.placeOrder` for `order.fees` payment: [4](#0-3) 

And the docs explicitly flag the underlying off-chain quoting mechanism as sandwich-prone, confirming there is no on-chain mitigation: [5](#0-4) [6](#0-5) 

### Title
Unbounded native-to-fee-token swap on `EvmHost.dispatch()`/`fundRequest()` and `IntentGatewayV2.placeOrder()` enables sandwich-attack value extraction from any dispatcher paying fees in native token - (File: `evm/src/core/EvmHost.sol`)

### Summary
Any unprivileged caller of `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, `fundRequest()`, or `IntentGatewayV2.placeOrder()` who pays the relayer/protocol fee with native token (`msg.value > 0`) triggers an on-chain `swapETHForExactTokens` against the configured `uniswapV2` router. The only bound on the swap's execution price is the caller's `msg.value`, which callers determine off-chain via `HyperApp.quote()`/`getAmountsIn`. There is no independently-specified maximum-input or minimum-rate parameter that reverts safely on manipulated pricing rather than executing at a degraded rate up to the full `msg.value`.

### Finding Description
`EvmHost.dispatch(DispatchPost)` and its GET/`fundRequest` counterparts execute:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
``` [1](#0-0) 

`swapETHForExactTokens` computes the required WETH input from the pool's *current* reserves at execution time and consumes up to `msg.value` of it — there is no application-level minimum output-rate check, and the "slippage bound" is simply whatever `msg.value` the caller happened to attach (typically derived from an off-chain `quote()` call moments earlier). This is functionally identical to the SushiMaker `convert()` bug class: a state-changing, unprivileged, AMM-routed swap with no protocol-enforced slippage protection independent of pool state at execution time.

An attacker (a searcher/relayer with mempool visibility, or the transaction submitter itself via a bundle) can:
1. Front-run the victim's `dispatch`/`fundRequest`/`placeOrder` call by trading against the `feeToken/WETH` pool to push the effective price of `feeToken` up in WETH terms.
2. Let the victim's `swapETHForExactTokens` execute at this degraded rate — it still succeeds as long as the manipulated cost stays at or under the victim's `msg.value`, silently consuming more of the victim's ETH than the fair-market rate would require.
3. Back-run by reversing the price manipulation, capturing the spread as MEV profit extracted directly from the fee-paying dispatcher.

The documentation acknowledges the underlying quoting primitive is sandwichable but the on-chain dispatch path has no independent protection against it — the caller cannot supply a tighter bound than "all of `msg.value`," so the manipulated-price window between quoting and execution is fully exploitable. [5](#0-4) [4](#0-3) 

### Impact Explanation
Every dispatcher paying Hyperbridge fees in native token — including ordinary users of `HyperApp`-based apps, `IntentGatewayV2` order placers, and integrators calling `fundRequest` — is exposed to MEV extraction proportional to the pool's manipulability and the caller's `msg.value` buffer over the fair quote. Because these entry points are permissionless, high-frequency, and directly reachable from a single submitted transaction, this constitutes concrete, repeatable value theft from unprivileged users of the core dispatch path (Medium/High depending on pool liquidity depth and fee-token trading volume).

### Likelihood Explanation
High: the swap is triggered on every native-token-funded `dispatch`/`fundRequest`/`placeOrder` call, requires no special privileges, and off-the-shelf sandwich bots already target unprotected Uniswap V2 router calls of this shape. The documentation's own warning about `quote()`'s sandwich exposure indicates the maintainers are aware the pricing input is manipulable, yet no on-chain slippage guard independent of `msg.value` exists.

### Recommendation
Add an explicit, caller-supplied maximum native input (or minimum acceptable rate) distinct from the raw `msg.value`, and revert if the router's actual required input exceeds it by more than an allowed tolerance, rather than letting `msg.value` alone serve as the slippage bound. Consider also refunding any unused `msg.value` (from `swapETHForExactTokens`) back to the original caller rather than leaving it in `address(this)`, and/or exposing a same-block TWAP or oracle-checked minimum rate for the swap, matching the pattern the `SimplexPaymaster.swapAndDeposit` already uses (oracle-derived `amountOutMin`).

### Proof of Concept
1. Attacker observes a pending `EvmHost.dispatch(DispatchPost)` (or `fundRequest`/`IntentGatewayV2.placeOrder`) transaction with `msg.value` computed from an off-chain `quote()` call.
2. Attacker front-runs it with a swap that sells WETH into the `feeToken/WETH` pool, raising the WETH cost of `feeToken`.
3. Victim's `swapETHForExactTokens{value: msg.value}(post.fee, ...)` executes at the degraded rate, consuming a larger share of `msg.value` for the same `post.fee` amount of tokens than the honest quote implied.
4. Attacker back-runs by buying back WETH from the pool, netting the price-impact spread as profit — funded by the victim's dispatch transaction.

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L70-80)
```text
    /**
     * @dev returns the quoted fee in the native token for dispatching a POST request
     */
    function quote(DispatchPost memory request) public returns (uint256) {
        address _host = host();
        address _uniswap = IDispatcher(_host).uniswapV2Router();
        address[] memory path = new address[](2);
        path[0] = IUniswapV2Router02(_uniswap).WETH();
        path[1] = IDispatcher(_host).feeToken();
        return IUniswapV2Router02(_uniswap).getAmountsIn(request.fee, path)[0];
    }
```
