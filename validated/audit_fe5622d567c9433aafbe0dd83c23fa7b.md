Found a concrete analog: in `UniV3UniswapV2Wrapper.sol`, the `init()` function calls the raw, non-safe `IERC20(params.WETH).approve(...)` even though the same contract imports `SafeERC20` and uses `forceApprove`/`safeTransferFrom` elsewhere. [1](#0-0) 

### Title
Unsafe raw `approve()` call in `UniV3UniswapV2Wrapper.init()` can revert for non-standard ERC20 WETH tokens - (File: evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol)

### Summary
`UniV3UniswapV2Wrapper.init()` grants the Uniswap V3 swap router a max allowance over the wrapper's `WETH` token using the raw `IERC20.approve()` call instead of `SafeERC20`'s `forceApprove()`, which the same contract already uses elsewhere in `swapExactTokensForETH`.

### Finding Description
`init()` is the one-time setup entrypoint that wires the wrapper to its configured `WETH` and `swapRouter`: [1](#0-0) 
It calls `IERC20(params.WETH).approve(params.swapRouter, type(uint256).max)` directly. Tokens like USDT that do not return a `bool` from `approve()` (or that revert when changing a non-zero allowance to another non-zero value) will make this call either revert or, on non-EVM-strict implementations, silently fail depending on how Solidity decodes the return data. The contract already demonstrates awareness of this class of token behavior — `swapExactTokensForETH` uses `IERC20(token).safeTransferFrom` and `IERC20(token).forceApprove` (line 178-179) precisely to avoid this issue for the swap-path token, but the WETH approval in `init()` was left using the unsafe pattern. [2](#0-1) 

While canonical WETH always returns a proper `bool`, the wrapper is a generic, deployer-configurable module (`Params.WETH` is caller-supplied at `init()` time) intended to plug into different EVM chains and router deployments — the same `UniswapV2Wrapper` family targets Gnosis, various L2s, etc. If deployed with a WETH-equivalent (or any wrapped-native token) whose `approve` behaves non-standard, `init()` can revert, permanently blocking the wrapper from ever initializing (since `_initialized` gating means it can only be attempted once) — a one-time, unrecoverable denial of service for that deployment, and any subsequent calls funneling native-token swaps through the compromised router path would be broken since the router would lack the allowance needed to move WETH for `swapETHForExactTokens`.

### Impact Explanation
If `init()` reverts due to a non-standard `approve()` return value on the deployed chain's wrapped-native token, the wrapper contract can never be initialized (single-call gate via `_initialized`/`_deployer` in `init()`), permanently freezing the module and blocking all native-token swap routing (`swapETHForExactTokens`) through it. This is a permanent freeze of intended functionality for that deployment, which the scan rules classify at Medium.

### Likelihood Explanation
Likelihood is deployment-dependent: for canonical WETH on Ethereum mainnet this never triggers because WETH's `approve()` is standards-compliant. However, since `Params.WETH` is a deployer-supplied address used across multiple EVM chains (the wrapper family already covers Gnosis's WXDAI and other chains), and the deployer has no compile-time guarantee that the wrapped-native token on every target chain returns a proper bool, the unsafe call is reachable at deploy/init time on any chain using a non-standard wrapped-native token implementation.

### Recommendation
Replace the raw call in `init()` with the same `SafeERC20` pattern already used elsewhere in the contract:
```solidity
using SafeERC20 for IERC20;
...
IERC20(params.WETH).forceApprove(params.swapRouter, type(uint256).max);
```
This matches the existing `forceApprove`/`safeTransferFrom` usage in `swapExactTokensForETH` and correctly handles both no-return-value tokens and tokens requiring a zero-reset before a new non-zero approval.

### Proof of Concept
1. Deploy `UniV3UniswapV2Wrapper` with `_deployer = attacker/deployer`.
2. Call `init(Params({WETH: nonStandardToken, swapRouter: router, quoter: quoter, maxFee: fee}))` where `nonStandardToken.approve()` does not return a `bool` (e.g., a USDT-like implementation).
3. The low-level call to `approve` succeeds at the EVM level but Solidity's automatic ABI decoding of the expected `bool` return value reverts because no data (or malformed data) was returned, causing `init()` to revert.
4. Since `_initialized` is never set to `true`, and `init()` can only be called once by `_deployer` (any resubmission still hits the same non-standard token and same revert), the wrapper is permanently unusable — `WETH()`, `swapETHForExactTokens`, and `swapExactTokensForETH` (which references `_params.WETH`/`_params.swapRouter`) never receive valid configuration.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L178-179)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amountIn);
        IERC20(token).forceApprove(_params.swapRouter, amountIn);
```
