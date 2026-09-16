## Title
Uniswap swap deadline set to `block.timestamp` provides no timestamp protection, exposing native-fee payers to stale-price execution — (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all swap native ETH for `feeToken` via Uniswap V2 using `block.timestamp` as the swap `deadline` argument, and the same pattern is duplicated in `IntentGatewayV2.placeOrder`'s fee-swap path. This is the on-chain equivalent of the reported `MeritDutchAuction` issue: passing `block.timestamp` as a deadline is a no-op, since whichever block ultimately includes the transaction will always satisfy `deadline >= block.timestamp`. There is no way for the caller to bound how long the transaction may sit unexecuted before the swap is settled.

### Finding Description
Any unprivileged user calling `dispatch()` with `msg.value > 0` triggers: [1](#0-0) 

The same construction repeats for GET dispatch and `fundRequest`: [2](#0-1) [3](#0-2) 

and again in the app-level fee-escrow path in `IntentGatewayV2.placeOrder`: [4](#0-3) 

Because `deadline = block.timestamp` is evaluated inside the swap call itself, it can never be exceeded — the check `require(deadline >= block.timestamp)` inside Uniswap's router is always true regardless of how long the transaction lingers in the mempool (held by a builder/relayer, resubmitted with low gas, delayed by network congestion, etc.). This removes the entire purpose of the `deadline` parameter: bounding the staleness of the price the swap executes against.

### Impact Explanation
`swapETHForExactTokens` fixes the *token* output (`post.fee`/`get.fee`/`order.fees`) but not the ETH input; the amount of ETH actually consumed is determined by the AMM's reserves **at execution time**, not at submission time. A user (or an intent placer/gateway relayer) computing `msg.value` off a quote taken when they signed the transaction has no on-chain guarantee that the swap executes near that price:
- If the transaction is delayed until ETH/feeToken pricing has moved unfavorably, the router will pull up to the full `msg.value` at the worse rate with no cap or revert threshold tied to time, silently overcharging the payer in ETH terms for the same fixed `feeToken` output.
- Because there is no `deadline` bound, this cannot be prevented by the caller — the only protection Uniswap's API offers for this exact class of risk is rendered inert.

This affects every path that lets a caller pay Hyperbridge dispatch/relayer fees in native token — a core, unprivileged, permissionlessly-reachable primitive (`EvmHost.dispatch`, `EvmHost.fundRequest`, `IntentGatewayV2.placeOrder`) — so it is a protocol-wide fee-payment integrity issue rather than an isolated one-off.

### Likelihood Explanation
Any user or MEV-aware actor can trigger this simply by holding/delaying inclusion of a `dispatch`/`fundRequest`/`placeOrder` transaction (e.g., via private mempools, low gas price, or sandwich/back-running around the swap), and the on-chain code offers no mechanism to reject a stale-priced execution. No special privileges are required — this is reachable from a single submitted transaction as required by the validation criteria.

### Recommendation
Replace `block.timestamp` with a caller-supplied `deadline` parameter (propagated through `DispatchPost`/`DispatchGet`/`fundRequest`/`Order.fees` swap paths) so callers can bound the maximum staleness they are willing to accept, consistent with standard Uniswap integration guidance. Optionally also cap acceptable slippage on the ETH side (e.g., a caller-provided `maxAmountIn` distinct from `msg.value`) so a stale/adverse price move reverts rather than silently consuming more ETH than intended.

### Proof of Concept
1. User A calls `EvmHost.dispatch(DispatchPost)` with `msg.value = X` computed against the current Uniswap V2 pool price, expecting to pay `post.fee` in `feeToken` using approximately `X` ETH.
2. The transaction is delayed in the mempool (e.g., low priority fee, private relay holding it, or a validator/searcher intentionally delaying inclusion) while the ETH/feeToken pool price moves against ETH.
3. When finally included, `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` still executes because `deadline == block.timestamp` at inclusion time trivially satisfies the router's check — it never reverts due to staleness.
4. The swap consumes ETH at the now-worse rate (up to the full `msg.value`), and User A receives no refund/revert protection based on how much time elapsed, having effectively overpaid for the same fixed `feeToken` amount with no recourse.

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

**File:** evm/src/core/EvmHost.sol (L1031-1039)
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
```

**File:** evm/src/apps/IntentGatewayV2.sol (L375-386)
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
```
