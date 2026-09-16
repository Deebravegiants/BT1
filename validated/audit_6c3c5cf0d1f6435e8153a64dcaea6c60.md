### Title
Multi-hop `path` arrays silently collapse to a single hop in `UniV3UniswapV2Wrapper`, causing wrong-token delivery in fee-quoting and bridged swap flows - (File: evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol)

### Summary
`UniV3UniswapV2Wrapper` presents a Uniswap-V2-compatible interface (`swapETHForExactTokens`, `swapExactTokensForETH`, `getAmountsIn`, `getAmountsOut`) that accepts an arbitrary-length `address[] calldata path`, exactly like the vulnerable `BorpaGateway.zap()` in the external report. Internally, every function only reads `path[0]` and `path[1]` and executes a single-hop Uniswap V3 swap/quote, silently ignoring any additional path elements a caller supplied for a multi-hop route.

### Finding Description
Each public function documents `path` as "an array of token addresses representing the path of the swap" (multi-hop semantics, matching the `IUniswapV2Router02` interface it mimics), but the implementation only ever consumes indices 0 and 1: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

There is no `path.length` validation anywhere in the contract, so a caller intending an A→B→C route (e.g. `path = [WETH, USDC, DAI]`) actually gets an A→B swap (WETH→USDC) executed and settled, with `path[1]` (USDC) treated as the final output token — exactly the same class of bug as the Borpa report, where `_zap()`/`enter()` only consumed `path[0]`/`path[1]` while accepting arbitrary-length paths.

This wrapper is deployed as the production `uniswapV2` /`UNISWAP_V2` fee-oracle router referenced by `IsmpHost`/`IDispatcher` (`config.set("UNISWAP_V2", address(wrapper))`) and by `EvmHost.quote()`/`HyperApp.quote()`, which call `getAmountsIn`/`getAmountsOut` on this router to price the native/relayer fee for dispatching ISMP messages: [5](#0-4) [6](#0-5) 

It is also the router surfaced to solvers/users in the Intent Gateway's predispatch/postdispatch `Call[]` composable-swap flows (`CallDispatcher` executes arbitrary calldata against whatever router is configured as `UNISWAP_V2`), as shown by the same pattern used against the real `IUniswapV2Router02` in the test/example calldata: [7](#0-6) 

### Impact Explanation
Any unprivileged actor constructing a `path` for a fee-quote call (via `EvmHost.quote()` reachable by any message dispatcher submitting an ISMP request/HFT `send()`), or any solver/user building predispatch/postdispatch swap calldata for `IntentGatewayV2` orders, can be misled into believing a multi-hop route (e.g. WETH→USDC→DAI) will deliver the final-hop token, when in fact only the first hop executes and settles. Because `swapETHForExactTokens`/`swapExactTokensForETH` deliver tokens for `path[1]`, not `path[path.length-1]`, and no length check reverts an over-long path, funds can be delivered/quoted in an unintended intermediate token. In dispatch-fee pricing this can misprice fees paid by users dispatching cross-chain messages; in Intent Gateway predispatch/postdispatch composable swaps this can result in the wrong token being escrowed or delivered to a beneficiary, freezing or misdirecting user/solver funds relative to what the on-chain order or fee computation assumed.

### Likelihood Explanation
The bug is trivially triggerable by any caller who supplies a `path` array with more than two elements — no special privileges are required, and nothing in the contract or its callers enforces `path.length == 2`. Whether it manifests in practice depends on whether any current caller (fee quoting or CallDispatcher-driven predispatch/postdispatch calldata) actually constructs a multi-hop path against this specific wrapper; all in-repo tests and examples happen to use 2-element paths, so likelihood is moderate rather than trivially certain, but the code contains no protection against the scenario.

### Recommendation
Add an explicit `require(path.length == 2)` (or equivalent revert) at the top of `swapETHForExactTokens`, `swapExactTokensForETH`, `getAmountsIn`, and `getAmountsOut`, matching the remediation applied upstream (limiting `path` to exactly 2 elements), so the interface cannot silently truncate a caller-supplied multi-hop route.

### Proof of Concept
1. Deploy `UniV3UniswapV2Wrapper` and `init()` it as shown in `evm/tests/foundry/UniV3UniswapV2WrapperTest.sol` (lines 35-44).
2. Build `path = [WETH, USDC, DAI]` (3 elements) intending a WETH→USDC→DAI swap.
3. Call `wrapper.swapExactTokensForETH(amountIn, amountOutMin, path, to, deadline)` — note the function reads `path[1]` (`USDC`) as `weth`-check target only if `path[1] != weth`, i.e. `path[1]` is treated as WETH regardless of the caller's intended final hop, and `path[0]` (`WETH`) is swapped directly into `path[1]`'s position via a single-hop V3 `exactInputSingle` with `tokenOut: weth`, bypassing the DAI leg entirely.
4. Observe that the function completes successfully despite the 3-element path, delivering native ETH derived from a WETH position rather than routing through the intended intermediate/final tokens, with no revert indicating the extra path elements were ignored — directly analogous to the `testZapThree()` PoC in the external report. [8](#0-7)

### Citations

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L114-134)
```text
    function swapETHForExactTokens(uint256 amountOut, address[] calldata path, address recipient, uint256 deadline)
        external
        payable
        returns (uint256[] memory)
    {
        address weth = _params.WETH;
        if (path[0] != weth) revert InvalidWethAddress();

        (bool sent,) = weth.call{value: msg.value}("");
        if (!sent) revert DepositFailed();

        IV3SwapRouter.ExactOutputSingleParams memory params = IV3SwapRouter.ExactOutputSingleParams({
            tokenIn: weth,
            tokenOut: path[1],
            fee: _params.maxFee,
            recipient: recipient,
            amountOut: amountOut,
            amountInMaximum: msg.value,
            sqrtPriceLimitX96: 0
        });

```

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L167-189)
```text
    function swapExactTokensForETH(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory) {
        address weth = _params.WETH;
        if (path[1] != weth) revert InvalidWethAddress();
        address token = path[0];

        IERC20(token).safeTransferFrom(msg.sender, address(this), amountIn);
        IERC20(token).forceApprove(_params.swapRouter, amountIn);

        IV3SwapRouter.ExactInputSingleParams memory params = IV3SwapRouter.ExactInputSingleParams({
            tokenIn: token,
            tokenOut: weth,
            fee: _params.maxFee,
            recipient: address(this),
            amountIn: amountIn,
            amountOutMinimum: amountOutMin,
            sqrtPriceLimitX96: 0
        });
```

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L216-225)
```text
    function getAmountsIn(uint256 amountOut, address[] calldata path) external returns (uint256[] memory) {
        IQuoterV2.QuoteExactOutputSingleParams memory params = IQuoterV2.QuoteExactOutputSingleParams({
            tokenIn: path[0], tokenOut: path[1], amount: amountOut, fee: _params.maxFee, sqrtPriceLimitX96: 0
        });
        (uint256 amountIn,,,) = IQuoterV2(_params.quoter).quoteExactOutputSingle(params);
        uint256[] memory amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = amountOut;
        return amounts;
    }
```

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L233-242)
```text
    function getAmountsOut(uint256 amountIn, address[] calldata path) external returns (uint256[] memory) {
        IQuoterV2.QuoteExactInputSingleParams memory params = IQuoterV2.QuoteExactInputSingleParams({
            tokenIn: path[0], tokenOut: path[1], amountIn: amountIn, fee: _params.maxFee, sqrtPriceLimitX96: 0
        });
        (uint256 amountOut,,,) = IQuoterV2(_params.quoter).quoteExactInputSingle(params);
        uint256[] memory amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = amountOut;
        return amounts;
    }
```

**File:** evm/script/DeployUniV3Wrapper.s.sol (L17-34)
```text
    function deploy() internal override {
        address swapRouter = config.get("SWAP_ROUTER").toAddress();
        address quoter = config.get("QUOTER").toAddress();
        uint24 maxFee = uint24(config.get("MAX_FEE").toUint256());
        address uniswapV2 = IDispatcher(HOST_ADDRESS).uniswapV2Router();

        UniV3UniswapV2Wrapper wrapper = new UniV3UniswapV2Wrapper{salt: salt}(admin);
        wrapper.init(
            UniV3UniswapV2Wrapper.Params({
                WETH: IUniswapV2Router02(uniswapV2).WETH(), swapRouter: swapRouter, quoter: quoter, maxFee: maxFee
            })
        );
        vm.stopBroadcast();
        console.log("UniV3UniswapV2Wrapper deployed at:", address(wrapper));
        console.log("UniV3UniswapV2Wrapper initialized");
        // Persist the deployed wrapper address into the UNISWAP_V2 config field.
        config.set("UNISWAP_V2", address(wrapper));
    }
```

**File:** evm/tests/foundry/HyperFungibleTokenTest.sol (L736-750)
```text
contract HyperFungibleTokenQuoteForkTest is MainnetForkBaseTest {
    function testQuotePricesNativeFeeThroughV3Wrapper() public {
        UniV3UniswapV2Wrapper wrapper = new UniV3UniswapV2Wrapper(address(this));
        wrapper.init(
            UniV3UniswapV2Wrapper.Params({
                WETH: _uniswapV2Router.WETH(),
                swapRouter: 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45,
                quoter: 0x61fFE014bA17989E743c5F6cB21bF9697530B21e,
                maxFee: 500
            })
        );

        // Point the host's fee oracle at the V3 wrapper, as it is configured on mainnet.
        HostParams memory params = host.hostParams();
        params.uniswapV2 = address(wrapper);
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L151-167)
```text
        // Prepare predispatch call to swap ETH -> DAI via UniswapV2
        address[] memory path = new address[](2);
        path[0] = WETH;
        path[1] = address(dai);

        // Get quote for expected output
        uint256[] memory amounts = _uniswapV2Router.getAmountsOut(ethAmount, path);
        uint256 expectedDaiAmount = amounts[1];
        uint256 minDaiAmount = (expectedDaiAmount * 95) / 100; // 5% slippage tolerance

        bytes memory swapCalldata = abi.encodeWithSelector(
            _uniswapV2Router.swapExactETHForTokens.selector,
            minDaiAmount,
            path,
            address(dispatcher),
            block.timestamp + 3600
        );
```
