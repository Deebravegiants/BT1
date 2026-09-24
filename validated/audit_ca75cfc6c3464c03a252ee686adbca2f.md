## Analysis

CVE‑2017‑13751 is a *reachable assertion abort* — a defensive check the code assumes can never fire, but which an attacker can actually trigger, causing an unrecoverable DoS. The direct analog in this codebase is `Router.OverflowCapDegenerate()` in `_computeBuy`, which the protocol's own documentation and tests explicitly assume is unreachable — an assumption that a plain unprivileged ERC20 donation breaks.

### Title
Direct Token donation to `Pair` breaks the `tokenReserve > tokenBalance` invariant, permanently bricking `Router.buy`/`_computeBuy`'s overflow-cap path - (File: `packages/contracts/src/Router.sol`)

### Summary
`Router._computeBuy` caps oversized buys at the pair's *real* token balance and back-calculates a capped virtual reserve: `cappedReserveToken = reserveToken - tokensOut`, reverting with `OverflowCapDegenerate` if that quantity is zero [1](#0-0) . The protocol's own invariant tests state this branch is unreachable *only* because `pair.tokenBalance() < pair.tokenReserve()` is assumed to hold at every state of the curve [2](#0-1) . That assumption relies on `tokenReserve` and `tokenBalance` moving in lock-step through `Pair.swap` [3](#0-2) , but a raw ERC20 `transfer` of the launched `Token` directly to the `Pair` address inflates `tokenBalance()` (a live `balanceOf` read, `Pair.tokenBalance()` at [4](#0-3) ) without touching the stored `_pool.tokenReserve`, closing or inverting the gap.

### Finding Description
At launch, `Bonding._deployAndSeed` seeds the pair with a virtual `tokenReserve = totalSupply` (1B) while only `curveSupply = 75%` (750M) is really transferred, leaving a permanent 250M (`LP_RESERVE`) gap between the two [5](#0-4) .

Every buy/sell through `Router` moves `tokenReserve` and the real `tokenBalance` by the *same* amount via `Pair.swap` (`newTokenReserve = pool.tokenReserve + tokenIn - tokenOut`), so the 250M gap is preserved through ordinary trading [3](#0-2) .

The attack:
1. An unprivileged trader buys `X` tokens off the curve via `Zap.buy`/`Bonding.buy` → `Router.buy`, where `250M < X < 750M`. Because the USD graduation trigger and the supply trigger are calibrated to both bind near full curve drain (~750M sold ≈ `$9K` threshold, per the protocol's own math: `USD raised = VIRTUAL_LIQUIDITY_USD × X/(1e9−X)`), buying ~250–300M tokens stays well below the graduation threshold, so `canGraduate` remains `false` and no `_enterGraduating` fires.
2. Both `reserveToken` and `tokenBalance` drop by `X` (gap unchanged, still 250M).
3. The attacker then sends those same `X` tokens straight back to the `Pair` address via `Token.transfer(pair, X)` — a plain ERC20 transfer that bypasses `Router`/`Pair.swap` entirely (nothing gates transfers *to* the pair; only `Router`-mediated moves update `_pool.tokenReserve`).
4. `tokenBalance()` rises back by `X`, but the stored `_pool.tokenReserve` is untouched. The gap becomes `250M − X`, which is **negative** once `X > 250M`.
5. Any subsequent buy that trips the overflow-cap branch in `_computeBuy` now computes `tokensOut = realBalance ≥ reserveToken`, so `cappedReserveToken = reserveToken - tokensOut` either underflows (Solidity `Panic(0x11)`) or, if exactly equal, explicitly reverts with `OverflowCapDegenerate()` [6](#0-5) .

Because `_pool.tokenReserve` was permanently shrunk relative to the real balance, this isn't a one-off revert: the pair is left in a state where the constant-product curve's virtual/real relationship is corrupted, and every buy sized past the (now much smaller) remaining headroom on that shrunken virtual reserve continues to hit the same broken branch. Since the buy path (`Bonding.buy` → `Router.buy`) is the *only* way a curve can ever cross the graduation threshold, an attacker who wants to permanently freeze a specific token's curve before it can graduate can donate enough tokens back to push the pair into this degenerate state, permanently trapping the raised LT and the 250M `LP_RESERVE` tokens inside `Bonding`/`Pair` with no path to `_enterGraduating`/`finalizeGraduation`, and freezing every trader who still holds curve tokens or wants to buy.

### Impact Explanation
This is a permanent freeze of protocol and trader funds: the curve-raised LT sitting in the `Pair`, the 250M `LP_RESERVE` tokens parked for graduation, and any trader tokens still purchasable on the curve become unreachable once the invariant is broken and buys start reverting. Unlike the documented "brick resistance" guarantees for `finalizeGraduation`, there is no equivalent defense for this pre-graduation donation path — the code's own test suite states the defensive `OverflowCapDegenerate` branch is assumed structurally unreachable, which is exactly the false assumption this attack exploits, mirroring CVE‑2017‑13751's "reachable assertion abort" DoS class.

### Likelihood Explanation
High. The steps require only: (1) a normal permissionless buy through `Zap.buy`/`Bonding.buy` sized between roughly 33% and 99% of `curveSupply` (well documented as safely below the graduation threshold), and (2) a plain `Token.transfer` of the purchased tokens back to the `Pair` address — both are ordinary transactions any unprivileged wallet can submit, with no special timing, front-running, or privileged role needed.

### Recommendation
`Router._computeBuy`'s overflow-cap logic must not rely on an assumed invariant between the stored virtual `tokenReserve` and the live `tokenBalance()`. Either derive `tokensOut`'s cap without depending on that gap remaining positive (e.g., re-derive the effective virtual reserve from `k` and the real balance each time, or track a separate "donated" surplus that is excluded from the cap math), or unconditionally sweep/burn any Token balance in the `Pair` that exceeds `_pool.tokenReserve` before it can be used in `_computeBuy`'s capping arithmetic, so a direct donation can never desynchronize the two values.

### Proof of Concept
1. Launch token `T` against LT `L` via `Bonding.launch`/`Zap.createToken` (standard seeding: `tokenReserve = 1e9`, real `curveSupply = 750e6`).
2. As `trader`, call `Zap.buy(T, usdcAmount, 0, address(0))` sized so that `Bonding.buy` returns `tokensOut ≈ 300e6` (comfortably under the ~750e6 needed to graduate).
3. As `trader`, call `T.transfer(pairAddress, 300e6 * 1e18)` — a plain ERC20 donation directly to the `Pair` contract.
4. Read `IPair(pair).getReserves()` and `IPair(pair).tokenBalance()`: `tokenBalance() > tokenReserve`, i.e., the invariant asserted in `test_inv_virtualReserveAlwaysExceedsRealBalance` [7](#0-6)  is now false.
5. Submit another oversized buy through `Zap.buy`/`Bonding.buy` that would trip `Router._computeBuy`'s cap branch; observe the transaction revert with `OverflowCapDegenerate()` (or an arithmetic underflow panic), and confirm the token's curve can no longer process the buy sizes needed to reach `canGraduate() == true`, permanently freezing that curve's raised LT and reserved LP tokens.

### Citations

**File:** packages/contracts/src/Router.sol (L127-148)
```text
    function _computeBuy(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 amountInUsed, uint256 tokensOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        amountInUsed = amountIn;

        uint256 newReserveAsset = reserveAsset + amountInUsed;
        tokensOut = reserveToken - (k / newReserveAsset);

        uint256 realBalance = pair.tokenBalance();
        if (tokensOut > realBalance) {
            tokensOut = realBalance;
            uint256 cappedReserveToken = reserveToken - tokensOut;
            if (cappedReserveToken == 0) revert OverflowCapDegenerate();
            uint256 cappedReserveAsset = (k + cappedReserveToken - 1) / cappedReserveToken;
            amountInUsed = cappedReserveAsset - reserveAsset;
        }
    }
```

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-377)
```text
    // ─── 8. Virtual reserve invariant (tokenBalance < tokenReserve) ──────

    /// @dev Production seeding (`virtualReserveToken = totalSupply`,
    ///      `realTokenAmount = curveSupply = 75% * totalSupply`) makes
    ///      `pair.tokenBalance() < pair.tokenReserve()` a hard property at
    ///      every state of the curve. This invariant is what makes the
    ///      `cappedReserveToken == 0` branch in `Router._computeBuy`
    ///      unreachable; if it ever ceased to hold, that branch would
    ///      revert with `OverflowCapDegenerate` rather than over-pay.
    function test_inv_virtualReserveAlwaysExceedsRealBalance() public {
        (address tokenAddr, address pairAddr) = _launchNoSeed();

        // Right after launch.
        assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "post-launch invariant");

        // After a series of buys the property must continue to hold while
        // the curve is still trading.
        for (uint256 i = 0; i < 10; i++) {
            if (!bonding.isTrading(tokenAddr)) break;
            _buy(tokenAddr, trader, 100 ether);
            if (bonding.isTrading(tokenAddr)) {
                assertTrue(IPair(pairAddr).tokenBalance() < _reserve0(pairAddr), "invariant must hold after every buy");
            }
        }
    }
```

**File:** packages/contracts/src/Pair.sol (L65-79)
```text
    function swap(
        uint256 tokenIn,
        uint256 tokenOut,
        uint256 assetIn,
        uint256 assetOut
    ) external onlyRouter returns (bool) {
        uint256 newTokenReserve = (_pool.tokenReserve + tokenIn) - tokenOut;
        uint256 newAssetReserve = (_pool.assetReserve + assetIn) - assetOut;
        if ((newTokenReserve + 1) * (newAssetReserve + 1) < _pool.k) revert KInvariantViolated();

        _pool.tokenReserve = newTokenReserve;
        _pool.assetReserve = newAssetReserve;
        emit Swap(tokenIn, tokenOut, assetIn, assetOut);
        return true;
    }
```

**File:** packages/contracts/src/Pair.sol (L103-105)
```text
    function tokenBalance() external view returns (uint256) {
        return IERC20(launchedToken).balanceOf(address(this));
    }
```

**File:** packages/contracts/src/Bonding.sol (L472-494)
```text
        uint256 totalSupply = Token(tokenAddr).TOTAL_SUPPLY();
        uint256 curveSupply = (totalSupply * CURVE_BPS) / BPS_DENOM;

        pair = $.factory.createPair(tokenAddr, ltAddress);

        uint256 exchangeRate = IBounceLeveragedToken(ltAddress).exchangeRate();
        if (exchangeRate == 0) revert ZeroExchangeRate();
        uint256 virtualLtReserve = (VIRTUAL_LIQUIDITY_USD * 1e18) / exchangeRate;
        // The raised LT reserve peaks at `3 * virtualLtReserve` (curve sell-out)
        // and is later deposited into a HyperSwap V2 pair, whose reserves are
        // `uint112`. Bound it at launch (4x headroom) so graduation can never
        // exceed that slot.
        if (virtualLtReserve > type(uint112).max / 4) revert ExchangeRateTooLow();

        IERC20(tokenAddr).forceApprove(address($.router), curveSupply);
        // Virtual tokenReserve = full totalSupply; only curveSupply (75%) actually transferred.
        // The launch-time `virtualLtReserve` is recoverable later as
        // `Pair.k() / Token.TOTAL_SUPPLY()`: `Pair.mint` sets `_pool.k =
        // tokenReserve * assetReserve = totalSupply * virtualLtReserve` once
        // and `Pair.swap` never modifies `_pool.k`. That identity is what
        // `_launchTimeVirtualLtReserve` exploits to derive donation-immune
        // raised-LT in `canGraduate` and `_prepareGraduationLiquidity`.
        $.router.addInitialLiquidity(tokenAddr, totalSupply, curveSupply, virtualLtReserve);
```
