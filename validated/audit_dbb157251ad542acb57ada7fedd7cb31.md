## Title
`EvmHost` native-fee swaps use `block.timestamp` as the Uniswap deadline, providing no real expiration protection - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all swap native token for `feeToken` via `IUniswapV2Router02.swapETHForExactTokens`, passing `block.timestamp` (the timestamp read at execution time) as the `deadline` argument instead of a bounded future deadline signed by the caller. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
Uniswap's `deadline` parameter is meant to bound how long a signed transaction may legitimately wait in the mempool before execution, protecting the sender from having their swap filled at a stale/manipulated price. Here `block.timestamp` is evaluated inside the `dispatch`/`fundRequest` call itself, so the "deadline" passed to the router is always equal to the actual execution timestamp — the router's `require(deadline >= block.timestamp)` check is therefore always trivially true, regardless of how long the transaction actually sat in the mempool or how the network's ETH/feeToken pool price changed in the meantime. This is functionally identical to having no deadline check at all, matching the reported "No Expiration Deadline" bug class.

Any unprivileged caller dispatching a POST/GET request or funding an existing request with native token value (`msg.value > 0`) goes through this code path, so the affected functions are directly reachable by ordinary message dispatchers with no special privileges.

### Impact Explanation
Because the effective deadline offers no real time-bound protection, a transaction paying the relayer fee in native token can be delayed by a searcher/validator and executed once the on-chain AMM price has been pushed unfavorably (e.g., via a sandwich attack around the `swapETHForExactTokens` call). Since the swap is "exact output" (`post.fee`/`get.fee`/`amount`) with the implicit maximum input bounded only by the full `msg.value` supplied, an attacker can manipulate pool price immediately before this swap executes and extract the difference between the fair-market ETH cost and the higher cost paid by the dispatcher, up to the full `msg.value` sent. This results in direct loss of user/dispatcher funds during ordinary, permissionless usage of `EvmHost` dispatch operations — one of the core, unprivileged entry points listed in scope.

### Likelihood Explanation
Every dispatcher that funds a POST/GET request (or increases its fee) with native ETH instead of pre-approved feeToken triggers this code path, and MEV searchers routinely monitor mempools for exactly this kind of unprotected AMM interaction (fixed deadline == execution time, exact-output swap with generous slippage bound equal to `msg.value`). No special conditions or governance/admin actions are required — a single ordinary `dispatch{value: ...}` call is sufficient to be exposed.

### Recommendation
Add a genuine, caller-supplied `deadline` parameter (or a fixed short window, e.g. `block.timestamp + X minutes`, computed and bound at signing time via a separate parameter passed by the caller) instead of re-deriving `block.timestamp` inside the function body. Additionally, allow the caller to specify a maximum acceptable native-token input (`amountInMax`) tighter than the full `msg.value`, so a delayed/sandwiched execution reverts rather than silently consuming more ETH than intended.

### Proof of Concept
1. A user calls `EvmHost.dispatch(DispatchPost)` with `msg.value` set to the amount they are willing to pay for `post.fee` worth of `feeToken` at current market rates, per [1](#0-0) .
2. The transaction is observed in the mempool and delayed (e.g., low gas price, or deliberately held by a searcher who front-runs/back-runs it).
3. Because the deadline passed to `swapETHForExactTokens` is computed as `block.timestamp` at actual execution time (not the time the user intended), the deadline check in the router is always satisfied no matter how long the transaction was delayed or how the pool price moved.
4. A searcher sandwiches the swap: front-run to move the ETH/feeToken price unfavorably, letting the exact-output swap consume close to the full `msg.value` to obtain `post.fee` tokens, then back-run to restore price and capture the difference as profit — extracted directly from the dispatching user's funds.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-929)
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
