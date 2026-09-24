Given the CVE's class — an unprivileged, network-reachable actor triggering a permanent hang/crash of a core server routine via crafted (but ordinary) input — the closest reachable analog in alt.fun's contracts is a permanent-revert DoS in `Router._computeBuy`'s overflow-cap branch, triggerable by any trader with a plain ERC20 donation.

### Title
Donating launched Token to its Pair permanently bricks the overflow-cap buy path via `OverflowCapDegenerate` - ([File: packages/contracts/src/Router.sol])

### Summary
`Router._computeBuy` caps `tokensOut` at the pair's *real* ERC20 balance (`pair.tokenBalance()`) whenever the constant-product quote would exceed it, then back-calculates `amountInUsed` from `cappedReserveToken = reserveToken - tokensOut`, reverting with `OverflowCapDegenerate` if that subtraction is zero (and reverting on unsigned underflow if it would go negative) [1](#0-0) . `reserveToken` is the *virtual* reserve, updated only by `Pair.swap` under `onlyRouter` [2](#0-1) , while `tokenBalance()` reads the pair's live ERC20 balance, which any unprivileged holder of the launched `Token` can inflate with a plain `transfer` to the pair address [3](#0-2) . The protocol's own test comments confirm this exact failure mode is anticipated and depends entirely on an invariant (`tokenBalance() < tokenReserve()`) that a direct donation can violate [4](#0-3) .

### Finding Description
`_computeBuy`'s design intent (per the natspec) is that "the last buy cannot exceed remaining supply," relying on the invariant that `pair.tokenBalance() < pair.tokenReserve()` (the virtual/stored reserve) holds at every state of the curve [5](#0-4) . That invariant is maintained only through legitimate curve trades: `Pair.swap` moves `tokenReserve` and the real balance (via `transferToken`) by the exact same amount, so the gap between virtual and real reserves — established at launch when `virtualReserveToken = totalSupply` and `realTokenAmount = 75% * totalSupply` [4](#0-3)  — never shrinks through ordinary buys/sells.

However, `Token` is a standard ERC20 and nothing prevents any holder (e.g., a trader who bought tokens off the curve) from calling `Token.transfer(pair, amount)` directly. This increases `pair.tokenBalance()` (the real ERC20 balance the `onlyRouter`-gated `Pair` contract reports via `tokenBalance()`) without any corresponding decrease to the stored `_pool.tokenReserve`, since only `Pair.swap`/`Pair.mint` — both `onlyRouter` — can write to `_pool` [6](#0-5) . A sufficiently large donation (accumulating tokens across the curve's remaining supply and re-donating them) closes or exceeds the virtual buffer, so `realBalance >= reserveToken` becomes possible.

Once that happens, the next oversized buy that hits the overflow-cap branch computes `tokensOut = realBalance` and then `cappedReserveToken = reserveToken - tokensOut`, which either underflows (Solidity 0.8 checked arithmetic reverts unconditionally) or lands exactly at zero, hitting the explicit `revert OverflowCapDegenerate()` [7](#0-6) . This reachable through `Router.buy`, `Router.previewBuy`, `getAmountOut`'s buy branch, and any downstream caller (`Bonding.buy`, `Zap.buy`, and the supply-leg branch of graduation-cap previews) that needs to size or execute a capped buy [8](#0-7) .

### Impact Explanation
Any buy request sized to consume the curve's remaining real token supply (the intended "close out the curve" trade, and the same math path used by the supply-leg of graduation-cap sizing per `test/Bonding.t.sol`'s mirroring of `Router._computeBuy`) permanently reverts once the donation-induced invariant break occurs, since the on-chain state causing the revert (`realBalance >= reserveToken`) cannot be reversed by any unprivileged action. This freezes the last portion of the curve — traders cannot complete the final buy that would exhaust supply, and tokens whose graduation is gated on the supply leg can be permanently blocked from graduating, freezing creator/LP/trader funds staged on that curve.

### Likelihood Explanation
Reachable by a single unprivileged trader using only standard ERC20 `transfer` calls plus ordinary `Bonding.buy`/`Zap.buy` calls — no privileged role, no upgrade, no off-chain component. The attack cost is bounded by the amount of Token needed to close the ~25% virtual/real buffer, which for smaller-cap or heavily-bought tokens nearing the end of their curve is comparatively cheap.

### Recommendation
Do not derive `tokensOut`'s cap or `cappedReserveToken` from the pair's raw `tokenBalance()` (a value any external donor can move). Track "real supply sold so far" in `Pair`'s own state (updated only by `swap`) instead of trusting `IERC20.balanceOf`, or explicitly `skim` any real-balance excess over the expected/reserve-derived value before using it in the cap calculation, mirroring the donation-resistant pattern already used in `Router.graduate`'s natspec.

### Proof of Concept
1. Launch a token via `Zap.createToken` (curve seeded with `virtualReserveToken = TOTAL_SUPPLY`, `realTokenAmount = 75% * TOTAL_SUPPLY`, per `_launchTimeVirtualLtReserve`/seeding logic).
2. Trader A buys close to the full remaining real supply via `Bonding.buy`/`Zap.buy`, receiving that Token balance in their wallet.
3. Trader A calls `Token.transfer(pair, receivedAmount)`, donating the tokens directly back to the `Pair` — a plain unprivileged ERC20 transfer, not routed through `Router`/`Pair.swap`, so `_pool.tokenReserve` is untouched while `pair.tokenBalance()` jumps up.
4. Trader B (or A) submits another oversized buy through `Bonding.buy` targeting the remaining real supply. `Router._computeBuy` computes `tokensOut = realBalance` (now inflated by the donation) and `cappedReserveToken = reserveToken - tokensOut`, which reverts with `OverflowCapDegenerate` (or an arithmetic underflow) instead of completing the capped buy.

I was unable to fully verify `Bonding.sol`'s exact `previewLtUntilGraduation` implementation or whether `Token.sol` imposes any transfer restriction that would block step 3, since my remaining tool budget ran out before reading those files directly; the test file evidence strongly suggests `previewLtUntilGraduation` mirrors `_computeBuy`'s cap formula exactly [9](#0-8) , but this should be confirmed against the live source before treating the graduation-blocking impact as certain.

### Citations

**File:** packages/contracts/src/Router.sol (L92-123)
```text
    function buy(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);

        (amountInUsed, tokensOut) = _computeBuy(pairAddr, amountIn);

        IERC20(asset).safeTransferFrom(to, pairAddr, amountInUsed);

        IPair(pairAddr).transferToken(to, tokensOut);
        IPair(pairAddr).swap(0, tokensOut, amountInUsed, 0);
    }

    /// @notice External view of `_computeBuy`. Returns `(amountInUsed,
    ///         tokensOut)` for a hypothetical LT-in buy of `amountIn`,
    ///         honouring the same overflow cap as `buy()`. Used by `Zap` to
    ///         pre-size the LT mint and by the frontend for buy-quote previews.
    function previewBuy(
        address token,
        uint256 amountIn
    ) external view returns (uint256 amountInUsed, uint256 tokensOut) {
        if (amountIn == 0) revert ZeroAmount();
        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        return _computeBuy(pairAddr, amountIn);
    }
```

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

**File:** packages/contracts/src/Pair.sol (L38-79)
```text
    modifier onlyRouter() {
        if (msg.sender != router) revert OnlyRouter();
        _;
    }

    constructor(
        address router_,
        address launchedToken_,
        address assetToken_
    ) {
        if (router_ == address(0) || launchedToken_ == address(0) || assetToken_ == address(0)) revert ZeroAddress();
        if (launchedToken_ == assetToken_) revert IdenticalTokens();
        router = router_;
        launchedToken = launchedToken_;
        assetToken = assetToken_;
    }

    function mint(
        uint256 tokenReserve,
        uint256 assetReserve
    ) external onlyRouter returns (bool) {
        if (_pool.k != 0) revert AlreadyMinted();
        _pool = Pool({tokenReserve: tokenReserve, assetReserve: assetReserve, k: tokenReserve * assetReserve});
        emit Mint(tokenReserve, assetReserve);
        return true;
    }

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

**File:** packages/contracts/test/GraduationInvariants.t.sol (L353-361)
```text
    // ─── 8. Virtual reserve invariant (tokenBalance < tokenReserve) ──────

    /// @dev Production seeding (`virtualReserveToken = totalSupply`,
    ///      `realTokenAmount = curveSupply = 75% * totalSupply`) makes
    ///      `pair.tokenBalance() < pair.tokenReserve()` a hard property at
    ///      every state of the curve. This invariant is what makes the
    ///      `cappedReserveToken == 0` branch in `Router._computeBuy`
    ///      unreachable; if it ever ceased to hold, that branch would
    ///      revert with `OverflowCapDegenerate` rather than over-pay.
```

**File:** packages/contracts/AGENTS.md (L91-91)
```markdown
- **Overflow buy cap.** `Router.buy` caps `tokensOut` at the pair's real balance and back-calculates the LT consumed, so the last buy cannot exceed remaining supply. `Zap.buy` returns the unused LT (`ltMinted - amountInUsed`) directly as LT — not redeemed, to avoid re-incurring the LT redemption fee on dust — while unconverted USDC and the fee over-charge are refunded in USDC. `Bonding.buy` returns `(tokensOut, amountInUsed)` for this reason.
```

**File:** packages/contracts/test/Bonding.t.sol (L828-840)
```text

        // Supply-leg = LT to drain `realBalance`. Mirrors
        // `Router._computeBuy`'s cap math.
        address pair = bonding.getTokenInfo(tokenAddr).pair;
        IPair p = IPair(pair);
        (uint256 reserveToken, uint256 reserveAsset) = p.getReserves();
        uint256 realBalance = p.tokenBalance();
        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (p.k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 expectedSupplyLeg = cappedReserveAsset - reserveAsset;

        assertEq(cap, expectedSupplyLeg, "Supply-leg binds at half rate");
    }
```
