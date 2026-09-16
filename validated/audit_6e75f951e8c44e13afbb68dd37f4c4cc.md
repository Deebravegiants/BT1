### Title
`block.timestamp` deadline in `EvmHost` fee-swap logic provides no MEV/staleness protection - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all perform a `swapETHForExactTokens` call using `block.timestamp` as the swap `deadline`. Because the deadline is derived from the same `block.timestamp` at which the swap actually executes, the deadline check inside the router can never fail — it provides zero protection against a relayer/validator delaying inclusion of the dispatching transaction to a more favorable (for them) point in time, exactly the bug class described in the reference report (using `block.timestamp`-derived values as a deadline is meaningless since it always resolves true at execution time).

### Finding Description
When a user calls `EvmHost.dispatch(DispatchPost memory post)` or `EvmHost.dispatch(DispatchGet memory get)` with `msg.value > 0`, the host swaps native ETH for the fee token via the local Uniswap V2 router, and passes `block.timestamp` as the deadline: [1](#0-0) 

The same pattern appears in the GET dispatch path and in `fundRequest`: [2](#0-1) [3](#0-2) 

`dispatch` and `fundRequest` are both externally callable by any unprivileged sender (`notFrozen` is the only modifier), making this a directly reachable dispatch-path issue rather than an admin-only concern. Because the `deadline` parameter equals `block.timestamp` at the moment the swap executes (not a value chosen ahead of time by the caller), the underlying router's `require(deadline >= block.timestamp)` check is trivially satisfied regardless of how long the outer transaction sat in the mempool before being included. This means the deadline offers no actual staleness protection: a block producer or searcher can hold the transaction and only include it once the AMM pool price has moved unfavorably (e.g., after their own manipulative trades), and the swap will still proceed. The same anti-pattern is repeated in `IntentGatewayV2.placeOrder`'s fee-swap logic: [4](#0-3) 

and in `SimplexPaymaster.swapAndDeposit`: [5](#0-4) 

### Impact Explanation
The fee-payment swaps convert native ETH supplied by message dispatchers into the protocol `feeToken`, and are on the critical path for `EvmHost.dispatch`/`fundRequest`, which every relayer, application, or end user relies on to pay for cross-chain message delivery. Because the deadline provides no real timing protection, a malicious searcher/validator can time-delay inclusion of `dispatch`/`fundRequest` transactions to coincide with adverse pool conditions they've engineered (e.g., via a preceding manipulative trade), causing the dispatcher to receive a worse `feeToken` amount than expected, or exhaust more ETH than necessary for the same fee — a direct value-extraction vector against message senders funding cross-chain dispatch.

### Likelihood Explanation
Any address can trigger the vulnerable code path simply by calling `dispatch` with `msg.value > 0` or `fundRequest` with `msg.value > 0`; no privileged role or special conditions are required. MEV searchers are already highly incentivized to monitor mempools for exactly this kind of predictable, deadline-less AMM interaction, so exploitation is realistic in production given sufficient trade volume.

### Recommendation
Do not derive the swap `deadline` from `block.timestamp` at execution time. Either accept a user/caller-supplied `deadline` parameter (propagated from `DispatchPost`/`DispatchGet`/`fundRequest` call sites) that reflects the time the caller actually signed/submitted the transaction, or remove the deadline mechanism's false sense of security by combining a caller-chosen `amountInMaximum`/`amountOutMinimum` slippage bound with a deadline value set independently of the current execution context.

### Proof of Concept
1. Attacker (validator/searcher) observes a pending `EvmHost.dispatch(DispatchPost)` call with `msg.value > 0` in the mempool.
2. Attacker manipulates the ETH/feeToken pool price via a sandwich trade, then withholds inclusion of the victim's `dispatch` transaction until the pool is in the attacker's favor.
3. When finally included (at any later block), `deadline = block.timestamp` is computed fresh at execution, so the router's deadline check always passes — the swap executes at the attacker-manipulated price instead of reverting due to staleness.
4. The dispatcher's ETH is converted to `feeToken` at an unfavorable rate, and the attacker profits from the sandwich, all while the "deadline" parameter never once served its intended purpose.

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

**File:** evm/src/core/EvmHost.sol (L1031-1041)
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

**File:** evm/src/utils/SimplexPaymaster.sol (L454-480)
```text
    function swapAndDeposit(address token, uint256 amountIn) external {
        if (msg.sender != treasury) revert UnauthorizedCall();
        address router = IDispatcher(host()).uniswapV2Router();
        if (router == address(0)) revert InvalidRouter(router);
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

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

        uint256 deposited = address(this).balance;
        entryPoint().depositTo{value: deposited}(address(this));
        emit FeesRecycled(token, amountIn, amounts[1], deposited);
    }
```
