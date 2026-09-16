### Title
Native-token fee payment in `EvmHost.dispatch`/`fundRequest` performs an unprotected Uniswap V2 swap, exposing dispatchers to sandwich-attack value extraction - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all allow paying protocol/relayer fees with native token. When `msg.value > 0`, they immediately call `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)` to buy the exact `feeToken` amount needed. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
Each of these three functions is directly callable by any unprivileged address (or any `HyperApp`/contract dispatching a request) with `msg.value`. The only "slippage protection" for the `exactOutput`-style swap is the implicit `amountInMaximum` of `msg.value`, and `deadline: block.timestamp` provides no real protection since a sandwich attack executes within the same block (front-run + victim tx + back-run).

Because the price used to determine how much ETH is consumed to buy the fixed `fee`/`amount` of `feeToken` is read live from the Uniswap V2 pool at execution time, an attacker can:
1. Front-run the `dispatch`/`fundRequest` call by buying up `feeToken` (or otherwise moving the pool price) so that the WETH→feeToken price becomes unfavorable.
2. Let the victim's transaction execute `swapETHForExactTokens`, which will now need to spend far more ETH (up to the full `msg.value` supplied) to acquire the same fixed `fee` amount of `feeToken`.
3. Back-run to restore the pool price and capture the value extracted from the victim's excess ETH spend.

This mirrors exactly the bug class in the referenced report: an AMM swap executed on-chain with no independently-computed minimum-output/maximum-input bound and a `deadline` that offers no real protection, making it trivially sandwichable by MEV searchers/validators. In the referenced USSD report the `amountOutMinimum` was hardcoded to `0`; here the analogous protection (a meaningful `amountInMaximum` below `msg.value`, ideally derived from an oracle or TWAP) is likewise absent — the `amountInMaximum` is simply whatever ETH the caller happened to send, which provides no real bound tied to fair market price.

Since `EvmHost.dispatch`/`fundRequest` are core, high-traffic entry points used by essentially all dispatched POST/GET requests paid in native token (see `IDispatcher.dispatch`), this is a broadly reachable, single-transaction issue affecting any user or `HyperApp` paying dispatch fees in native token. [4](#0-3) 

### Impact Explanation
An MEV searcher/validator can systematically sandwich `EvmHost.dispatch`/`fundRequest` calls that pay fees in native token, extracting the difference between the fair-market ETH cost of the required `feeToken` amount and the manipulated (sandwiched) cost — up to the full `msg.value` provided by the caller. This is a direct value-extraction vector against every unprivileged user/app that pays dispatch or relayer fees in native token, causing concrete loss of funds on essentially every dispatch call that goes through this path. Given `dispatch`/`fundRequest` are the primary fee-payment entry points for the ISMP host (used by GET/POST requests, `TokenGateway`, `IntentGatewayV2`, and any `HyperApp`), the aggregate impact across the protocol is High.

### Likelihood Explanation
Likelihood is high: any transaction calling `dispatch`/`fundRequest` with `msg.value > 0` is visible in the mempool prior to inclusion, and Uniswap V2 pools are commonly thin enough to be manipulated profitably within a single block. No special privilege is required to exploit this — it is a standard MEV sandwich attack pattern executed by any searcher/validator monitoring the mempool.

### Recommendation
- Compute a proper `amountInMaximum` for `swapETHForExactTokens` derived from a manipulation-resistant price source (e.g., a TWAP oracle or Chainlink price feed, similar to the pattern already used in `SimplexPaymaster.swapAndDeposit`, which derives `amountOutMin` from Chainlink oracles rather than trusting the caller-supplied bound). [5](#0-4) 
- Reject the transaction if the on-chain swap would require more ETH than a bounded slippage percentage above the oracle-derived fair price, rather than allowing the full `msg.value` to be consumed.
- Consider using a real deadline (e.g., `block.timestamp + X`) is irrelevant to sandwich protection; the actual fix is bounding `amountInMaximum` to a value tied to an external price reference, not to `msg.value`.
- Alternatively, strongly recommend/require fee-token payment (bypassing the swap entirely) for any amount-sensitive or high-value dispatch, and clearly document the swap-based native payment path as inherently MEV-exposed (the existing docs already warn about `quote()` being sandwichable off-chain, but the on-chain `dispatch`/`fundRequest` swap itself needs the fix, not just a documentation caveat).

### Proof of Concept
1. Attacker monitors mempool for a pending `EvmHost.dispatch(DispatchPost)` (or `dispatch(DispatchGet)`/`fundRequest`) call with `msg.value > 0` targeting a WETH/feeToken Uniswap V2 pool with limited liquidity.
2. Attacker front-runs with a large WETH→feeToken buy, sharply increasing the feeToken price in WETH terms.
3. Victim's `dispatch` executes `swapETHForExactTokens{value: msg.value}(post.fee, [WETH, feeToken], address(this), block.timestamp)` — since the pool price is now unfavorable, the router consumes a much larger fraction of `msg.value` to acquire the same fixed `post.fee` amount of `feeToken`. [6](#0-5) 
4. Attacker back-runs by selling feeToken back for WETH, restoring the pool price and pocketing the ETH difference extracted from the victim's transaction.
5. The victim ends up paying substantially more ETH than fair market value for the same `feeToken` fee amount, with no recourse since the swap already completed atomically within the `dispatch` call.

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

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L118-131)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the IHost.feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the IHost.feeToken.
     *
     * @param request - post request
     * @return commitment - the request commitment
     */
    function dispatch(DispatchPost memory request) external payable returns (bytes32 commitment);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L447-475)
```text
    /// @dev The minimum output is derived onchain from the Chainlink oracles
    ///      (markup-free price minus `swapSlippageBps`), so the caller cannot
    ///      influence the execution price. Still treasury-gated: were this
    ///      permissionless, a UserOp's calldata could invoke it mid-bundle and
    ///      swap away other ops' pending prefunds, breaking their postOp
    ///      refunds. The treasury sends ordinary transactions, which can never
    ///      execute mid-bundle.
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
```
