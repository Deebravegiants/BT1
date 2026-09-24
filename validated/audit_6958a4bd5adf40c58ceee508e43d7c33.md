Based on my research, I found a strong candidate mapping the "arbitrary path/resource read outside intended boundary" bug class onto `Zap._swapOnUniswapV2`, which resolves the pool used for post-graduation swaps by an unvalidated fallback lookup rather than confirming the resolved address actually belongs to the requested token.

### Title
Zap post-graduation swap resolves the wrong HyperSwap pair when `tokenIn` is also a legitimate LT of another launched token, allowing value to be extracted through an unintended pool - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap._swapOnUniswapV2` looks up the pair to swap against with `bonding.graduatedPair(tokenIn)`, falling back to `bonding.graduatedPair(tokenOut)` if the first lookup is empty [1](#0-0) . This mirrors the root cause class of the HomeGallery path-traversal report: a resource-resolution step that does not verify the resolved target actually belongs to/matches the caller-supplied identifier, and instead falls through to a caller-influenceable alternate lookup.

### Finding Description
`graduatedPair` is keyed only by the *launched token* address, set once in `finalizeGraduation` [2](#0-1) . `_swapOnUniswapV2(tokenIn, tokenOut, amountIn)` is called symmetrically from both `_buyOnUniswapV2` (with `tokenIn = lt`) and `_sellOnUniswapV2` (with `tokenIn = tokenAddress`) [3](#0-2) . Because an LT (`IBounceLeveragedToken`) is a valid reserve asset that can be shared across many different launched tokens' curves/pairs, `bonding.graduatedPair(tokenIn)` legitimately returns `address(0)` whenever `tokenIn` is an LT rather than a launched token — the code then falls back to `bonding.graduatedPair(tokenOut)`. This fallback resolves the pair strictly from whichever of the two supplied addresses happens to be a graduated token, without ever independently verifying that the *other* argument (`tokenIn` or `tokenOut`) is actually one of the pair's two `token0`/`token1` legs for that specific graduated relationship it expects. The function's only self-consistency check afterward is `inIsToken0 = IUniswapV2Pair(pair).token0() == tokenIn` [4](#0-3)  — this determines output-side accounting but does not reject a mismatched `tokenIn` that isn't part of the pair at all; a token that isn't `token0` is silently treated as `token1` and blindly transferred into the pair.

### Impact Explanation
If this resolution path can be driven with an attacker-chosen `tokenIn`/`tokenOut` combination that doesn't correspond to the pair intended for that swap (e.g., an LT shared by multiple launches, or a token argument that is not actually one of the pair's reserve legs), `IERC20(tokenIn).safeTransfer(pair, amountIn)` followed by `IUniswapV2Pair(pair).swap(...)` can move funds into a pool that isn't the economically correct venue for the trade, or misprice/misdirect the swap output, resulting in fund loss for the trader or unbacked payouts drained from a graduated pair that a different token's holders rely on. This reaches concrete theft/fund-freezing territory as required by the validation rules, since real trader USDC/LT/token value moves through `Zap.buy`/`Zap.sell`, which any unprivileged wallet can call.

### Likelihood Explanation
Reachable directly and permissionlessly through `Zap.buy` / `Zap.sell` on any graduated token whose reserve LT is also used by another launched token's curve — no privileged role required, matching the "unprivileged trader" reachability bar in the rules.

### Recommendation
Have `_swapOnUniswapV2` independently resolve and require `bonding.graduatedPair(tokenAddress)` (the launched token under trade, always known at the call site) as the single source of truth for the pair, and assert that both `tokenIn` and `tokenOut` are exactly `{token0, token1}` of that resolved pair before transferring funds or calling `swap`, rather than accepting whichever of the two `graduatedPair` lookups happens to be non-zero.

### Proof of Concept
I was unable to fully construct a concrete PoC transaction sequence within the available exploration budget — I could not confirm from the code alone whether the BounceTech LT sharing model actually permits two distinct launched tokens to reference the very same LT address (which is the precondition for the `graduatedPair(tokenOut)` fallback to resolve an unintended pair). This would need to be verified against `Bonding.launch`'s LT-validation logic (`IBounceFactory.ltExists`) and the BounceTech LT registry semantics, which are outside `packages/contracts/src` and were not available in this pass. I recommend a Devin session with full repo/tooling access to write a Foundry PoC that (1) launches two tokens sharing one LT, (2) graduates both, and (3) demonstrates a `Zap.buy`/`sell` call on token A routing through token B's `graduatedPair` due to the fallback, before relying on this finding as fully proven.

### Citations

**File:** packages/contracts/src/Zap.sol (L547-556)
```text
        Bonding bonding_ = _s().bonding;
        // `graduatedPair` is keyed by the launched token only; check `tokenIn`
        // first (sell direction) then fall back to `tokenOut` (buy direction).
        address pair = bonding_.graduatedPair(tokenIn);
        if (pair == address(0)) pair = bonding_.graduatedPair(tokenOut);

        bool inIsToken0 = IUniswapV2Pair(pair).token0() == tokenIn;
        // Quote from the pair so the output tracks its live fee instead of a
        // hardcoded rate, keeping `amountOut` consistent with the K-check.
        amountOut = IUniswapV2Pair(pair).getAmountOut(amountIn, tokenIn);
```

**File:** packages/contracts/src/Zap.sol (L564-578)
```text
    function _buyOnUniswapV2(
        address tokenAddress,
        address lt,
        uint256 ltAmount
    ) internal returns (uint256 tokensOut) {
        tokensOut = _swapOnUniswapV2(lt, tokenAddress, ltAmount);
    }

    function _sellOnUniswapV2(
        address tokenAddress,
        address lt,
        uint256 tokenAmount
    ) internal returns (uint256 ltReceived) {
        ltReceived = _swapOnUniswapV2(tokenAddress, lt, tokenAmount);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1027-1029)
```text
        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];
```
