### Title
Hardcoded single Uniswap V3 fee tier in `UniV3UniswapV2Wrapper` can permanently break native-ETH fee payment for `fundRequest`/`placeOrder` - (File: evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol)

### Summary
`UniV3UniswapV2Wrapper` is deployed and registered as the `uniswapV2Router` used across Hyperbridge (`EvmHost.fundRequest`, `IntentGatewayV2.placeOrder`) to let users pay message/order fees in native ETH instead of the ERC-20 fee token. Every swap it performs — `swapETHForExactTokens` and `swapExactTokensForETH` — uses one immutable, globally-fixed Uniswap V3 fee tier (`_params.maxFee`) for the WETH↔feeToken pair, regardless of which fee-tier pool actually has liquidity. This is the exact bug class from the referenced Beedle report: a fixed `fee` parameter passed to `ExactInputSingleParams`/`ExactOutputSingleParams` instead of dynamically selecting/parameterizing the correct pool tier.

### Finding Description
`UniV3UniswapV2Wrapper.Params.maxFee` is set once at `init()` time and never varies per call: [1](#0-0) 

Both swap entrypoints hardcode `fee: _params.maxFee` into the Uniswap V3 `ExactOutputSingleParams`/`ExactInputSingleParams` structs: [2](#0-1) [3](#0-2) 

The deploy script confirms `maxFee` is a single governance-set constant for the whole wrapper, and the wrapper's address is written directly into the host's `UNISWAP_V2` config slot (i.e., it becomes `IDispatcher(host).uniswapV2Router()`): [4](#0-3) 

This router is then invoked directly by unprivileged, permissionless entrypoints:

1. `EvmHost.fundRequest` — any caller can send native ETH to top up a request's relayer fee; the host swaps `msg.value` ETH for the exact `feeToken` amount through `uniswapV2` (the wrapper), using `swapETHForExactTokens`: [5](#0-4) 

2. `IntentGatewayV2.placeOrder` — when a user places an order with `order.fees > 0` and pays in native value, it performs the identical WETH→feeToken swap through the same `uniswapV2Router`: [6](#0-5) 

Because the wrapper hardcodes a single fee tier for every WETH↔token pair it is ever asked to swap, if the actual deepest/only liquid Uniswap V3 pool for the configured `feeToken` sits at a different tier (e.g. 500 or 10000 instead of the configured 3000, which is common — many token/WETH pairs are only liquid at one specific tier, and liquidity providers can migrate tiers over time), the `exactInputSingle`/`exactOutputSingle` calls will either revert outright (no pool at that fee) or execute against an illiquid/nonexistent pool, causing `fundRequest` and native-value `placeOrder` calls to permanently fail. This is unlike the SDK's off-chain quoting/execution helpers, which properly probe multiple fee tiers (`COMMON_FEE_TIERS`) and pick the best one — the on-chain wrapper has no equivalent fallback and cannot be worked around by callers, since the fee tier is baked into `Params` at `init()` and is not an input to any external function.

### Impact Explanation
Any change in Uniswap liquidity distribution away from the governance-configured `maxFee` tier permanently breaks the native-ETH funding rail for both `EvmHost.fundRequest` (used to top up under-funded cross-chain message relaying) and `IntentGatewayV2.placeOrder` (used by any user placing orders and paying with native currency). This is a "route unable to deliver messages" condition: relayers relying on `fundRequest` top-ups to get stuck requests delivered would have no on-chain path to pay in native ETH, and users who only hold native ETH (not the ERC-20 feeToken) cannot place orders at all — since there is no way to select an alternate fee tier without a contract redeploy and governance reconfiguration of the router address. This can silently persist for extended periods since nothing prevents the LP for the configured tier from being drained/moved after deployment.

### Likelihood Explanation
Liquidity migration across Uniswap V3 fee tiers is common and outside Hyperbridge's control; a feeToken/WETH pool at the configured tier draining to near-zero liquidity (or never having deep liquidity in the first place relative to other tiers) is a realistic, externally-triggerable condition, not an admin error. Any unprivileged user or relayer calling `fundRequest{value: ...}` or `placeOrder` with native value is affected once this occurs, with no code-level mitigation available to them.

### Recommendation
Do not hardcode a single `maxFee` for the wrapper's whole lifetime. Either:
- Accept the fee tier (or full path) as a parameter on `swapETHForExactTokens`/`swapExactTokensForETH`, letting the caller (or a periodically-updated `EvmHost`/`IntentGatewayV2` config) supply the correct tier per call, or
- Have the wrapper query `IQuoterV2` across the standard fee tiers (100/500/3000/10000) on-chain and route to whichever tier currently has sufficient liquidity/best price, mirroring the fallback logic already implemented off-chain in the SDK's `getV3QuoteWithAmountIn`.

### Proof of Concept
1. Governance deploys `UniV3UniswapV2Wrapper` with `maxFee = 3000` for `feeToken` = USDC, per `DeployUniV3Wrapper.s.sol`, and it is registered as `host.uniswapV2Router()`.
2. Uniswap V3 liquidity providers subsequently migrate WETH/USDC liquidity away from the 0.3% pool (or that pool simply never had material liquidity relative to the 0.05% pool, as is true for USDC/WETH on mainnet today).
3. A relayer calls `EvmHost.fundRequest{value: X}(commitment, amount)` to top up an under-funded request so it can be delivered. `swapETHForExactTokens` executes `exactOutputSingle` against the (now illiquid or nonexistent) 3000-fee pool and reverts (`STF`/pool not initialized), or executes at a far worse price than the 500-fee pool would offer, and can revert with `amountInMaximum` exceeded.
4. Every subsequent `fundRequest` and native-value `placeOrder` call fails identically until governance redeploys a new wrapper with the correct tier and updates the host's router address — during which time under-funded requests cannot be topped up via native ETH and native-value orders cannot be placed at all.

### Citations

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L35-44)
```text
    struct Params {
        /// @dev Address of the Wrapped Ether (WETH) token.
        address WETH;
        /// @dev Address of the Uniswap V3 Swap Router02.
        address swapRouter;
        /// @dev Address of the Uniswap V3 quoter contract
        address quoter;
        /// @dev The fees that helps point to the specific pool.
        uint24 maxFee;
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
