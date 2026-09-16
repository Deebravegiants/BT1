### Title
Hardcoded, immutable Uniswap fee-tier/pool-key in `UniV3UniswapV2Wrapper` / `UniV4UniswapV2Wrapper` forces all native-fee swaps through a single pool - (File: evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol, evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol)

### Summary
Both `UniV3UniswapV2Wrapper` and `UniV4UniswapV2Wrapper` are drop-in "Uniswap V2" adapters used by `EvmHost` (and downstream consumers like `HyperApp.quote()`, `HyperbridgeLzEndpoint`, and `SimplexPaymaster`) to swap native ETH for the protocol's `feeToken`. Both wrappers hardcode the pool selector (`_params.maxFee` for V3, `_params.defaultFee`/`defaultTickSpacing` for V4) once in `init()`, with no path to ever change it afterward, forcing every native-fee swap for the life of the contract through one specific fee-tier pool — exactly the "hardcoded pool(fee)" pattern from the reference report.

### Finding Description
`UniV3UniswapV2Wrapper.init()` stores an immutable `maxFee` in `_params` [1](#0-0) , which is then used unconditionally as the `fee` field for both the exact-output swap in `swapETHForExactTokens` [2](#0-1)  and the exact-input swap in `swapExactTokensForETH` [3](#0-2) , as well as both quoting helpers `getAmountsIn`/`getAmountsOut` [4](#0-3) . There is no setter for `_params.maxFee` after `init()` — `_initialized` permanently locks it.

The V4 wrapper has the identical pattern: `_createPoolKey()` always builds the `PoolKey` with the immutable `_params.defaultFee`/`defaultTickSpacing` [5](#0-4) , used by every swap and quote function in the contract [6](#0-5) , again set once and unchangeably in `init()` [7](#0-6) .

This wrapper is wired in as `_hostParams.uniswapV2` and is on the hot path for `EvmHost.dispatch()` and `EvmHost.fundRequest()` whenever a caller pays with native ETH instead of the fee token directly [8](#0-7) [9](#0-8) . It is also the quoting venue used by every `HyperApp`-derived application (`quote()` in the SDK base contract) [10](#0-9) , by `HyperbridgeLzEndpoint`'s native-fee path, and by `SimplexPaymaster.swapAndDeposit` for fee recycling [11](#0-10) .

Because the pool tier is fixed forever, if the market's liquidity for the WETH/feeToken pair migrates away from that specific fee tier (a routine occurrence in Uniswap V3/V4 markets), or if that tier's pool is comparatively thin, every native-ETH dispatcher is permanently forced to route through it: (a) if the tier's pool becomes illiquid or is never deployed, every native-ETH `dispatch()`/`fundRequest()` call reverts, cutting off the entire native-payment rail for message dispatch across the protocol; (b) if the tier's pool has materially less depth than alternate tiers, an unprivileged actor can economically target that single, known, immutable venue with sandwich/JIT-liquidity attacks against every incoming exact-output swap, since dispatchers have no ability to select a deeper pool.

### Impact Explanation
This is reachable by any unprivileged message dispatcher paying the relayer fee in native ETH via `EvmHost.dispatch()`/`fundRequest()`, or any app relying on `HyperApp.quote()`/`quoteNative()` for fee estimation, or `HyperbridgeLzEndpoint` OApp users paying in native token, or the paymaster's fee-recycling. A single unconfigurable pool tier means:
- A route that stops being able to deliver messages: once liquidity for the hardcoded tier dries up, native-ETH dispatch reverts protocol-wide with no on-chain remediation short of a full re-deployment and host reconfiguration.
- Concrete value loss to dispatchers: because the pool is fixed and publicly known, MEV searchers can reliably sandwich the exact-output swap in `swapETHForExactTokens`, extracting value from every fee-paying dispatcher who is forced into that single venue with no alternative route to select a deeper, less manipulable pool.

### Likelihood Explanation
Uniswap fee-tier liquidity migration across V3 fee tiers (and even more so nascent V4 pools) is common and outside the control of Hyperbridge; the wrapper offers no mechanism to adapt. Any dispatcher who pays fees with native ETH (a normal, first-class code path in `EvmHost.dispatch`/`fundRequest`) is affected, and the attack surface for sandwiching a fixed, known pool is straightforward for any bot monitoring `PostRequestEvent`/`RequestFunded` transactions.

### Recommendation
Do not hardcode the fee tier/pool key as an immutable constructor parameter with no update path. Either:
- Add a governance-gated setter (analogous to other `HostManager` parameter updates) allowing the fee tier/tick spacing to be updated without redeploying the wrapper and re-pointing `_hostParams.uniswapV2`, or
- Have the wrapper dynamically select the best available fee tier (analogous to the SDK's `getV4QuoteWithAmountIn` helper, which already iterates `COMMON_FEE_TIERS` off-chain) rather than pinning one tier on-chain forever, or
- Allow the caller to pass the desired fee tier explicitly as the original report recommends for `InfiltrationPeriphery`.

### Proof of Concept
1. `UniV3UniswapV2Wrapper` (or `UniV4UniswapV2Wrapper`) is deployed and `init()` is called once, hardcoding `maxFee = 3000` (or `defaultFee`/`defaultTickSpacing`) for the WETH/feeToken pair; it is then registered as `_hostParams.uniswapV2` on `EvmHost`.
2. Liquidity providers migrate the bulk of WETH/feeToken liquidity to a different fee tier (e.g. from 0.3% to 0.05%) over time, or the 0.3% pool is deliberately kept thin by an attacker.
3. Any user calling `EvmHost.dispatch{value: x}(post)` with `post.fee > 0` triggers `swapETHForExactTokens` against the fixed 0.3% pool [8](#0-7) . With thin liquidity, the price impact/slippage is far worse than in the deeper alternate-tier pool, and an attacker who monitors the mempool can sandwich the exact-output swap in the wrapper to extract value from the dispatcher's `msg.value`, since the dispatcher has no way to choose a different, deeper pool.
4. If the 0.3% pool's liquidity is fully withdrawn, every subsequent native-ETH `dispatch()`/`fundRequest()` call reverts permanently, since neither wrapper contract nor `EvmHost` exposes a way to change the pool selector without a full contract redeploy and host reconfiguration — a route unable to deliver messages until a privileged intervention occurs.

**Note on completeness:** I was not able to fully verify within this session whether `HostManager`/`EvmHost` exposes a privileged setter to swap out `_hostParams.uniswapV2` entirely (i.e., point to a freshly-deployed wrapper with a different hardcoded fee tier) as a mitigation path; if such a setter exists, the "unable to deliver messages" impact is recoverable only via a privileged governance action, not by any unprivileged party, but the value-extraction/sandwich exposure while it remains misconfigured, and the DoS window until governance reacts, still stand.

### Citations

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L90-97)
```text
    function init(Params memory params) public {
        if (_initialized || msg.sender != _deployer) revert Unauthorized();
        // approve the swap router to spend WETH
        IERC20(params.WETH).approve(params.swapRouter, type(uint256).max);

        _params = params;
        _initialized = true;
    }
```

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L125-133)
```text
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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L181-189)
```text
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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L216-242)
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

    /**
     * @notice Given an input amount of an asset and a path, returns the output amounts.
     * @param amountIn The amount of the asset you want to swap.
     * @param path An array of token addresses representing the path of the swap.
     * @return amounts An array of output amounts to be received.
     */
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

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L53-57)
```text
    function init(Params memory params) external {
        if (_initialized || msg.sender != _deployer) revert Unauthorized();
        _params = params;
        _initialized = true;
    }
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L66-165)
```text
    function swapETHForExactTokens(uint256 amountOut, address[] calldata path, address recipient, uint256 deadline)
        external
        payable
        returns (uint256[] memory amounts)
    {
        PoolKey memory poolKey = _createPoolKey(path[1]);

        bytes[] memory params = new bytes[](3);
        params[0] = abi.encode(poolKey, true, uint128(amountOut), uint128(msg.value), bytes(""));
        params[1] = abi.encode(poolKey.currency0, uint256(0), false);
        params[2] = abi.encode(poolKey.currency1, recipient, amountOut);

        bytes[] memory inputs = new bytes[](1);
        inputs[0] = abi.encode(
            abi.encodePacked(uint8(Actions.SWAP_EXACT_OUT_SINGLE), uint8(Actions.SETTLE), uint8(Actions.TAKE)), params
        );

        // Snapshot standing balance (excluding inbound msg.value) so the refund is the swap-call delta only,
        // immune to any ETH that lands on the wrapper from outside the router (e.g., selfdestruct, coinbase).
        uint256 balanceBefore = address(this).balance - msg.value;

        IUniversalRouter(_params.universalRouter).execute{value: msg.value}(
            abi.encodePacked(bytes1(uint8(Commands.V4_SWAP))), inputs, deadline
        );

        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
        }

        amounts = new uint256[](2);
        amounts[0] = msg.value - refundETH;
        amounts[1] = amountOut;
    }

    function swapExactTokensForETH(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts) {
        address token = path[0];
        PoolKey memory poolKey = _createPoolKey(token);

        // Stage the tokens on the router so SETTLE can pay them from its own balance.
        IERC20(token).safeTransferFrom(msg.sender, address(this), amountIn);
        IERC20(token).safeTransfer(_params.universalRouter, amountIn);

        bytes[] memory params = new bytes[](3);
        // token (currency1) -> ETH (currency0), so zeroForOne is false.
        params[0] = abi.encode(poolKey, false, uint128(amountIn), uint128(amountOutMin), bytes(""));
        params[1] = abi.encode(poolKey.currency1, uint256(0), false);
        params[2] = abi.encode(poolKey.currency0, to, uint256(0));

        bytes[] memory inputs = new bytes[](1);
        inputs[0] = abi.encode(
            abi.encodePacked(uint8(Actions.SWAP_EXACT_IN_SINGLE), uint8(Actions.SETTLE), uint8(Actions.TAKE)), params
        );

        uint256 balanceBefore = to.balance;

        IUniversalRouter(_params.universalRouter).execute(
            abi.encodePacked(bytes1(uint8(Commands.V4_SWAP))), inputs, deadline
        );

        amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = to.balance - balanceBefore;
    }

    function getAmountsIn(uint256 amountOut, address[] calldata path) external returns (uint256[] memory amounts) {
        address tokenOut = _isNativeToken(path[0]) ? path[1] : path[0];
        bool zeroForOne = _isNativeToken(path[0]);
        PoolKey memory poolKey = _createPoolKey(tokenOut);

        (uint256 amountIn,) = IV4Quoter(_params.quoter)
            .quoteExactOutputSingle(
                IV4Quoter.QuoteExactSingleParams(poolKey, zeroForOne, uint128(amountOut), bytes(""))
            );

        amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = amountOut;
    }

    function getAmountsOut(uint256 amountIn, address[] calldata path) external returns (uint256[] memory amounts) {
        address tokenOut = _isNativeToken(path[0]) ? path[1] : path[0];
        bool zeroForOne = _isNativeToken(path[0]);
        PoolKey memory poolKey = _createPoolKey(tokenOut);

        (uint256 amountOut,) = IV4Quoter(_params.quoter)
            .quoteExactInputSingle(IV4Quoter.QuoteExactSingleParams(poolKey, zeroForOne, uint128(amountIn), bytes("")));

        amounts = new uint256[](2);
        amounts[0] = amountIn;
        amounts[1] = amountOut;
    }
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L171-179)
```text
    function _createPoolKey(address tokenOut) internal view returns (PoolKey memory) {
        return PoolKey({
            currency0: Currency.wrap(address(0)), // ETH is always currency0
            currency1: Currency.wrap(tokenOut),
            fee: _params.defaultFee,
            tickSpacing: _params.defaultTickSpacing,
            hooks: IHooks(address(0))
        });
    }
```

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

**File:** evm/src/utils/SimplexPaymaster.sol (L440-480)
```text
    /// @notice Swaps accrued stablecoins to the native asset through the host's
    ///         V2-style router and deposits the contract's entire native balance
    ///         into the EntryPoint, so collected fees keep the paymaster funded
    ///         without a governance round-trip.
    /// @param token    A registered token; deactivated tokens remain recyclable.
    /// @param amountIn Token amount to swap; 0 (or more than the balance)
    ///                 swaps the full balance.
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

        uint256 deposited = address(this).balance;
        entryPoint().depositTo{value: deposited}(address(this));
        emit FeesRecycled(token, amountIn, amounts[1], deposited);
    }
```
