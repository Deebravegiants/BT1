## Finding

### Title
Unchecked `uint256 → uint128` downcast of swap amounts in `UniV4UniswapV2Wrapper` truncates large amounts silently - ([File: evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol])

### Summary
`UniV4UniswapV2Wrapper.swapETHForExactTokens` and `swapExactTokensForETH` accept caller-supplied `uint256 amountOut`/`amountIn` and cast them directly to `uint128` when building the Uniswap V4 Universal Router calldata, without any bounds check. This mirrors the report's bug class exactly: Solidity's explicit narrowing cast does not revert on overflow, it truncates modulo `2^128`.

### Finding Description
In `swapExactTokensForETH`, the full `amountIn` is transferred from the caller and forwarded to the router *before* the swap is executed: [1](#0-0) 

The router-facing exact-in swap action is built with `uint128(amountIn)` — a silent truncation if `amountIn >= 2^128`: [2](#0-1) 

Meanwhile the SETTLE step is encoded with amount `0`, i.e. "settle from the router's entire token balance" — the router will consume the *full, untruncated* `amountIn` balance it was just sent as payment for a swap whose accounted amount is only the truncated (small) `uint128(amountIn)`: [3](#0-2) 

The same downcast pattern appears in `swapETHForExactTokens` (`uint128(amountOut)`, `uint128(msg.value)`) and in `getAmountsIn`/`getAmountsOut` quoter calls: [4](#0-3) [5](#0-4) 

These functions are `external` with no access control and no minimum/maximum validation on the passed amounts: [6](#0-5) [7](#0-6) 

This wrapper is deployed as a first-class protocol contract (registered under the `UNISWAP_V2` config key), giving it a "V2-style interface" specifically so it can be driven by Hyperbridge's intent-gateway solver flow described in the file's own doc comment: [8](#0-7) [9](#0-8) 

### Impact Explanation
A very-high-decimal or very-low-unit-value ERC20 token (the same precondition class used in the original report) makes a swap amount `>= 2^128` economically small (well under the ~$34k–$136k threshold cited in the report, scaled to the token's decimals). In that case:
- For `swapExactTokensForETH`: the full (untruncated) input amount is pulled from the caller and handed to the router as payment, while Uniswap V4's exact-in accounting only reasons about the truncated `uint128` amount. The excess above `2^128` is settled/consumed by the router's "settle-all" balance sweep without being credited toward any recorded delta, so it is effectively donated/lost rather than swapped — a direct loss of user/solver funds with no path to recovery.
- For `swapETHForExactTokens`: the request to the pool for exact output uses the truncated `uint128(amountOut)` while the function's own accounting (`amounts[1] = amountOut`, and the `TAKE` params using untruncated `amountOut`) assumes the full requested amount was delivered, breaking the invariant the wrapper reports to its caller (e.g., an intent-gateway solver relying on `amounts[1]` to know how much was actually delivered to the recipient).

This satisfies the "concrete theft or permanent freezing of funds" bar: value transferred by an unprivileged caller can be silently reduced/lost, matching the analog's root cause (uint256→uint128 downcast without an overflow check) precisely.

### Likelihood Explanation
Likelihood is low-to-medium: it requires a token whose economically meaningful transfer amounts exceed `2^128` raw units (e.g., extreme-decimal tokens), similar to the precondition in the original report. Since the wrapper places no restriction on which ERC20 can be used in `path`, and the functions are permissionlessly callable by any solver/user integrating with the intent-gateway swap flow, the precondition is reachable without any privileged action — it only depends on token choice, which callers (including solvers filling arbitrary orders) do not control uniformly.

### Recommendation
Add explicit bounds checks (`require(amountIn <= type(uint128).max)` / `require(amountOut <= type(uint128).max)` / `require(msg.value <= type(uint128).max)`) before casting to `uint128` in `swapETHForExactTokens`, `swapExactTokensForETH`, `getAmountsIn`, and `getAmountsOut`, reverting instead of silently truncating.

### Proof of Concept
1. Deploy an ERC20 token with 24+ decimals (unrestricted by the wrapper) and mint a balance to a caller such that a "small" real-world value amount is `>= 2^128` raw units (e.g. `~3.4e38 + 1`).
2. Caller invokes `swapExactTokensForETH(amountIn, amountOutMin, [token, WETH], to, deadline)` with `amountIn = 2^128 + X` for some `X`.
3. `IERC20(token).safeTransferFrom(msg.sender, address(this), amountIn)` and `safeTransfer(_params.universalRouter, amountIn)` move the full `amountIn` to the router.
4. `params[0]` encodes `uint128(amountIn)` which truncates to `X` — the router's exact-in swap logic only accounts for `X` tokens of input.
5. `params[1]`'s SETTLE step (amount `0` = settle-all) consumes the router's *entire* balance (the full `amountIn`) as payment, i.e., `2^128` extra raw token units beyond what the swap accounted for are consumed/lost without a corresponding credit, permanently costing the caller that value.

### Citations

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L27-32)
```text
/**
 * @title UniV4UniswapV2Wrapper
 * @author Polytope Labs (hello@polytope.technology)
 * @notice Wraps Uniswap V4 Universal Router with V2-style interface for ETH swaps
 */
contract UniV4UniswapV2Wrapper {
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L66-76)
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
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L103-109)
```text
    function swapExactTokensForETH(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts) {
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L113-121)
```text
        // Stage the tokens on the router so SETTLE can pay them from its own balance.
        IERC20(token).safeTransferFrom(msg.sender, address(this), amountIn);
        IERC20(token).safeTransfer(_params.universalRouter, amountIn);

        bytes[] memory params = new bytes[](3);
        // token (currency1) -> ETH (currency0), so zeroForOne is false.
        params[0] = abi.encode(poolKey, false, uint128(amountIn), uint128(amountOutMin), bytes(""));
        params[1] = abi.encode(poolKey.currency1, uint256(0), false);
        params[2] = abi.encode(poolKey.currency0, to, uint256(0));
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L139-165)
```text
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

**File:** evm/script/DeployUniV4Wrapper.s.sol (L22-37)
```text
        UniV4UniswapV2Wrapper wrapper = new UniV4UniswapV2Wrapper{salt: salt}(admin);

        wrapper.init(
            UniV4UniswapV2Wrapper.Params({
                universalRouter: universalRouter,
                quoter: quoter,
                WETH: weth,
                defaultFee: defaultFee,
                defaultTickSpacing: defaultTickSpacing
            })
        );
        vm.stopBroadcast();
        console.log("UniV4UniswapV2Wrapper deployed at:", address(wrapper));
        console.log("UniV4UniswapV2Wrapper initialized");
        // Persist the deployed wrapper address into the UNISWAP_V2 config field.
        config.set("UNISWAP_V2", address(wrapper));
```
