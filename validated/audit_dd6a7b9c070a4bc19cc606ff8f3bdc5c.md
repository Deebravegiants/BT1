## Title
Swap deadline hardcoded to `block.timestamp` in `EvmHost` and `IntentGatewayV2` native-fee swaps enables indefinite mempool exposure and MEV extraction - (File: `evm/src/core/EvmHost.sol`, `evm/src/apps/IntentGatewayV2.sol`)

### Summary
Every fee-paying entry point in `EvmHost.sol` that accepts native token payment converts it to `feeToken()` via `IUniswapV2Router02.swapETHForExactTokens`, and hardcodes the swap `deadline` parameter to `block.timestamp` rather than a caller-supplied, bounded value [1](#0-0) . The same pattern appears in `dispatch(DispatchGet)` [2](#0-1) , `fundRequest` [3](#0-2) , and in `IntentGatewayV2.placeOrder`'s fee-swap logic [4](#0-3) . This mirrors exactly the reported bug class: `deadline` set to `block.timestamp` evaluates to "now" at whatever time the transaction is actually mined, so the deadline check is a permanent no-op regardless of how long the transaction has been pending.

### Finding Description
`dispatch(DispatchPost)` is a public, unrestricted (`notFrozen` only) entry point — any unprivileged message dispatcher can call it and pay the relayer fee with native ETH [5](#0-4) . When `msg.value > 0`, the function immediately performs a UniswapV2 `swapETHForExactTokens` with `deadline: block.timestamp`:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
``` [6](#0-5) 

Because Solidity evaluates `block.timestamp` at execution time (not at signing/broadcast time), this deadline can never actually expire — the resulting `deadline` argument always equals the timestamp of the block that includes the transaction. This defeats the entire purpose of a swap deadline, which exists to bound how long a signed/pending transaction can sit exposed to unfavorable price conditions or be deliberately withheld by a block producer/relayer/searcher before inclusion. A transaction using this pattern can be held in the mempool (or by a colluding builder/validator) indefinitely and only executed once market conditions or a sandwich setup are most profitable to the party controlling inclusion, with no expiry ever blocking it.

The identical unprotected pattern recurs in `dispatch(DispatchGet)` [7](#0-6) , in `fundRequest` (relayer-fee top-ups) [8](#0-7) , and in `IntentGatewayV2.placeOrder`, which performs the same swap to cover `order.fees` from user-supplied native value [9](#0-8) .

### Impact Explanation
Each of these swaps pays with the entire `msg.value`, and the router refunds any unspent ETH after routing the exact-output amount. With no effective deadline, a searcher/builder that observes the pending call can withhold it and sandwich the swap at a moment that maximizes the price the caller effectively pays (minimizing the refund the caller/protocol receives back), extracting value directly from the message dispatcher, intent submitter, or the protocol's fee-funding flow. This is a value-extraction (MEV) vector on every native-fee-funded dispatch, GET request, `fundRequest` top-up, and `IntentGatewayV2` order placement — core, high-traffic paths of Hyperbridge's message dispatch and intents systems.

### Likelihood Explanation
These functions are unrestricted and are the standard way any user or contract pays relayer fees in native token; they are called extremely frequently in normal operation, and the flawed deadline logic is unconditional (triggered any time `msg.value > 0`) rather than conditional on rare inputs, making the exposure window persistent across the protocol's normal usage.

### Recommendation
Accept an explicit, caller-supplied (or governance-configured, bounded) `deadline` parameter for all internal UniswapV2 fee-swap calls in `EvmHost.sol` (`dispatch(DispatchPost)`, `dispatch(DispatchGet)`, `fundRequest`) and in `IntentGatewayV2.placeOrder`, rather than hardcoding `block.timestamp`, so pending swaps cannot be withheld indefinitely before execution.

### Proof of Concept
1. A dispatcher calls `EvmHost.dispatch(DispatchPost)` with `msg.value > 0` to pay the relayer fee in native ETH [1](#0-0) .
2. The transaction is broadcast to the mempool; a block builder/searcher observing it delays inclusion and/or sandwiches the pool used by `uniswapV2` before including the transaction, since `deadline = block.timestamp` will always validate no matter when it is finally mined.
3. The victim's `swapETHForExactTokens` executes at the manipulated price, consuming more of `msg.value` than fair value and returning a smaller refund, with the difference captured by the attacker — all while the "deadline" protection never triggers a revert to prevent this.

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

**File:** evm/src/core/EvmHost.sol (L974-982)
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
