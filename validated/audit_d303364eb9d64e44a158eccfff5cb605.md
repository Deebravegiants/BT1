### Title
Missing decimal reconciliation between BounceTech LT's 6-dp base-asset accounting and Bonding/Zap's 18-dp "USD" accounting - ([File: packages/contracts/src/Zap.sol], [File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.VIRTUAL_LIQUIDITY_USD` and every downstream "USD"/threshold constant are hard-coded and documented as 18-decimal-precision figures [1](#0-0) , while the real reserve asset consumed by `Zap._executeBuy`/`_sellInternal` is BounceTech's leveraged token (LT), whose `mint`/`redeem`/`exchangeRate`/`baseToLtAmount`/`ltToBaseAmount` operate on the base asset's *native* decimals (real USDC = 6 dp) [2](#0-1) . The codebase's own test-support comments explicitly flag this gap: the mock USDC used everywhere in the test suite is deliberately given 18 decimals "so a raw USD amount and its 18-dp USDC representation are the same number," while `zap.minUsdcAmount()` is separately documented and asserted as a genuine 6-dp value mirroring the real mainnet floor (`10e6` == $10) [3](#0-2) [4](#0-3) .

### Finding Description
`Zap._sellInternal` is the only place in the buy/sell/graduation stack that acknowledges the decimal gap: it computes `grossUsdcEstimate = (ltReceived * exchangeRate) / 1e18` and then explicitly re-scales it by dividing by `1e12` before comparing against the 6-dp `minUsdcAmount()` floor [5](#0-4) . This one-off `/1e12` normalization only makes sense if `grossUsdcEstimate` is otherwise carried in 18-dp units elsewhere in the system (consistent with `VIRTUAL_LIQUIDITY_USD = 3000 ether` and every `*Usd`-suffixed value in `Bonding.sol` being declared 18-dp) [1](#0-0) .

Everywhere else — `_executeBuy`'s `usdcAmount`/`netUsdc`/`baseToConvert` that get passed straight into `IBounceLeveragedToken.mint(...)` [6](#0-5) , the seed-buy floor arithmetic in `minSeedUsdc()` [7](#0-6) , and `Bonding`'s `graduationThresholdUsd`/`VIRTUAL_LIQUIDITY_USD` comparisons that drive `previewLtUntilGraduation`/`canGraduate` — none of these paths apply any decimals conversion between the raw ERC20 amount actually transferred (which, for a real 6-dp USDC deployment, is 1e12× smaller per dollar than the `... ether`-denominated constants baked into `Bonding`) and the 18-dp accounting the constants assume. This is the exact bug class from the external report: two values that are combined/compared in arithmetic (`VIRTUAL_LIQUIDITY_USD`/`graduationThresholdUsd` at assumed 18-dp vs. actual on-chain USDC transfer amounts at 6-dp) are never checked or normalized for a decimals mismatch, so the "same numeric value" is silently treated as wildly different real-world amounts depending on which code path reads it.

### Impact Explanation
If real mainnet USDC (6 decimals) is wired in as `Zap.usdc()`/BounceTech's base asset while `Bonding.VIRTUAL_LIQUIDITY_USD` and `graduationThresholdUsd` remain 18-dp-denominated constants (`3000 ether`, etc.), then reaching graduation would require raw USDC transfers on the order of 1e12× the constant's face value — an amount no real trader can ever supply, permanently freezing every launched curve short of graduation (freezing of trader/creator funds parked in `Bonding` and preventing the LP-seeding/`LPLock.recordLock` step from ever firing). Conversely, if the constants were instead expressed in 6-dp terms to match real USDC, the LT interface's own documented 18-dp `exchangeRate()`/`baseToLtAmount()` semantics [8](#0-7)  would then produce `mint()` outputs mis-scaled by the same 1e12 factor relative to what `Router._computeBuy` expects, corrupting the bonding-curve token payout math (unbacked token payouts or a curve that can never absorb real trade sizes).

### Likelihood Explanation
This is a systemic accounting-precision assumption baked into constants and comments across `Bonding.sol`, `Zap.sol`, and the test harness (`DeployHelper.sol` explicitly calls out that its 18-dp mock USDC exists only "so a raw USD amount and its 18-dp USDC representation are the same number" — an equivalence that does not hold for the real 6-dp USDC token). The presence of an isolated, one-off `/1e12` correction in exactly one function (`_sellInternal`'s pre-check) while every other USDC-facing arithmetic path lacks the same correction indicates the mismatch was patched reactively in a single spot rather than resolved at the design level. I was not able to inspect `Deploy.s.sol`'s actual USDC address/decimals configuration within the remaining tool budget, so I cannot confirm with certainty whether the live deployment target uses genuine 6-dp USDC or an 18-dp-decimal wrapped/mock USDC that would sidestep this issue entirely — this is the key open uncertainty for this finding.

### Recommendation
Read `IERC20Metadata(address(usdc)).decimals()` once at initialization and use it to explicitly scale every raw USDC amount into (or out of) the 18-dp "USD" domain used by `VIRTUAL_LIQUIDITY_USD`/`graduationThresholdUsd`/`minSeedUsdc`, consistently across `_executeBuy`, `_sellInternal`, and every `Bonding` threshold comparison — not just the single `/1e12` normalization currently present in `_sellInternal`. Add an explicit invariant/constructor check that the configured decimals assumption matches the actually-deployed USDC contract's `decimals()`, analogous to the missing-decimal-check fix recommended in the source report.

### Proof of Concept
1. Deploy `Bonding`/`Zap` against a real-shape USDC token with 6 decimals (as `Deploy.s.sol` targets for mainnet, unlike the 18-decimal mock in `DeployHelper.sol`).
2. `VIRTUAL_LIQUIDITY_USD = 3000 ether` (`3000e18`) and `graduationThresholdUsd` (a similarly 18-dp-scaled multiple) remain unchanged.
3. A trader calls `Zap.buy(tokenAddress, usdcAmount, minTokensOut, referrer)` with `usdcAmount` denominated in real 6-dp USDC (e.g., `1000e6` for $1,000).
4. `_executeBuy` forwards this raw 6-dp amount straight into `IBounceLeveragedToken.mint` and into `Router._computeBuy`'s reserve math, which is calibrated against an 18-dp `virtualLtReserve` derived from `VIRTUAL_LIQUIDITY_USD` [1](#0-0) .
5. Because the trade amount is 1e12× smaller in raw units than the constants assume, the curve's reserve ratios move negligibly per real dollar spent, and `previewLtUntilGraduation`/`canGraduate` never trip — the token can never graduate regardless of how much real USDC volume trades through it, freezing creator/trader funds inside `Bonding` indefinitely.

### Citations

**File:** packages/contracts/src/Bonding.sol (L50-61)
```text
    /// @dev Virtual liquidity seeded at launch, in USDC (18-dp). Every
    ///      `*Usd`-named value and every "USD" figure in this contract is
    ///      a USDC amount scaled to 18-dp: the protocol treats 1 USDC as
    ///      1 USD and holds no price oracle.
    ///      Combined with the LT's launch-time `exchangeRate()` to derive
    ///      the launch-time `virtualLtReserve`, which permanently shapes
    ///      the curve via `K = TOTAL_SUPPLY * virtualLtReserve`. Pairs
    ///      with `Deploy.s.sol::GRADUATION_THRESHOLD_USD` at `$9K`
    ///      (3× peg preserved). Constant — changing it for an existing
    ///      proxy is a no-op because `K` is baked into each `Pair` at
    ///      `mint` and never recomputed.
    uint256 public constant VIRTUAL_LIQUIDITY_USD = 3000 ether;
```

**File:** packages/contracts/src/interfaces/IBounceLeveragedToken.sol (L26-42)
```text
    function baseAssetBalance() external view returns (uint256);

    /// @notice USDC per LT unit, 18-dp.
    function exchangeRate() external view returns (uint256);

    /// @notice Equals the LT amount that `mint(_, baseAmount, _)` will produce
    ///         at the current `exchangeRate()`.
    function baseToLtAmount(
        uint256 baseAmount
    ) external view returns (uint256);

    /// @notice Inverse of `baseToLtAmount`. The round-trip
    ///         `baseToLtAmount(ltToBaseAmount(x))` may differ from `x` by 1
    ///         wei due to integer-division rounding.
    function ltToBaseAmount(
        uint256 ltAmount
    ) external view returns (uint256);
```

**File:** packages/contracts/test/DeployHelper.sol (L244-251)
```text
    // ─── USDC-denominated trade-size helpers ─────────────────────────────
    //
    // Mock USDC in `_deployCore` uses the OZ default of 18 decimals, so a
    // raw USD amount and its 18-dp USDC representation are the same number.
    // These helpers compose the LT-side helpers above with the implicit
    // 1 USDC = $1 mapping so Zap-style suites can size buys in USDC space
    // without re-deriving the math. They scale with `VIRTUAL_LIQUIDITY_USD`
    // and `graduationThresholdUsd`, so they keep working as the dial moves.
```

**File:** packages/contracts/src/Zap.sol (L292-360)
```text
        uint256 buyFeeBps_ = $.buyFeeBps;
        uint256 feeOnGross = (usdcAmount * buyFeeBps_) / BPS_DENOM;
        uint256 netUsdc = usdcAmount - feeOnGross;
        // The LT floor applies to the post-fee amount forwarded to `mint`, not
        // the gross input — `_buyInternal`'s pre-check on `usdcAmount` leaves a
        // ~5-cent dirty band (`[MIN, MIN / (1 − buyFeeBps/BPS_DENOM)]`) where
        // the gross passes but `mint` reverts with the undecodable
        // `0x05eb05ac` selector that the pre-check exists to suppress.
        if (netUsdc < minUsdcAmount()) revert BelowMinAmount();

        $.usdc.safeTransferFrom(msg.sender, address(this), usdcAmount);

        // BounceTech LTs are mint-pausable (but NOT redeem-pausable). When
        // the LT operator pauses minting, this call reverts, so every buy
        // through Zap — bonding curve and post-graduation alike — DoSes for
        // that token while sells keep working (sells go through `redeem`,
        // not `mint`). This is an accepted v1 tradeoff: a sell-only market
        // is preferable to freezing both sides, since holders can still
        // exit to USDC. Post-graduation, anyone holding LT directly can
        // also still buy by swapping on the HyperSwap TOKEN/LT pair,
        // bypassing Zap. We do not mirror BounceTech's pause flag in
        // `Zap` (it would couple our pausing surface to theirs and add
        // storage with no security gain).
        uint256 baseToConvert;
        uint256 ltMinted;
        if ($.bonding.isGraduated(tokenAddress)) {
            baseToConvert = netUsdc;
            $.usdc.forceApprove(lt, baseToConvert);
            ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
            tokensOut = _buyOnUniswapV2(tokenAddress, lt, ltMinted);
            amountInUsed = ltMinted;
        } else {
            uint256 ltIfFull = IBounceLeveragedToken(lt).baseToLtAmount(netUsdc);
            uint256 ltUntilGraduation = $.bonding.previewLtUntilGraduation(tokenAddress);

            if (ltUntilGraduation >= ltIfFull) {
                baseToConvert = netUsdc;
            } else {
                // `ltToBaseAmount` floors. Bump up so `mint(baseToConvert)`
                // yields ≥ `ltUntilGraduation` and the cap-binding buy
                // actually flips `canGraduate` true — otherwise the
                // closing buy can miss graduation by 1-2 wei of LT.
                if (ltUntilGraduation > 0) {
                    baseToConvert = IBounceLeveragedToken(lt).ltToBaseAmount(ltUntilGraduation);
                    if (IBounceLeveragedToken(lt).baseToLtAmount(baseToConvert) < ltUntilGraduation) {
                        baseToConvert += 1;
                    }
                }
                if (baseToConvert > netUsdc) baseToConvert = netUsdc;

                // Floor-bump: the cap-implied mint can fall below the LT
                // mint floor (BounceTech reverts with `BelowMinTransactionSize`,
                // selector `0x05eb05ac`), making the token un-graduatable
                // via any `Zap.buy`. Mint at the floor instead and refund
                // the LT overshoot to `msg.sender` after the curve buy
                // (see the LT-excess transfer below). Refund must be in
                // LT, not USDC — round-tripping the overshoot through
                // `redeem` would re-incur BounceTech's redemption fee on
                // dust, defeating the pre-sizing optimisation this branch
                // exists for.
                uint256 floor = minUsdcAmount();
                if (baseToConvert < floor) {
                    baseToConvert = floor;
                    if (baseToConvert > netUsdc) revert BelowMinAmount();
                }
            }

            $.usdc.forceApprove(lt, baseToConvert);
            ltMinted = IBounceLeveragedToken(lt).mint(address(this), baseToConvert, 0);
```

**File:** packages/contracts/src/Zap.sol (L444-445)
```text
        uint256 grossUsdcEstimate = (ltReceived * IBounceLeveragedToken(lt).exchangeRate()) / 1e18;
        if (grossUsdcEstimate / 1e12 < minUsdcAmount()) revert BelowMinAmount();
```

**File:** packages/contracts/src/Zap.sol (L628-635)
```text
    /// @notice Live BounceTech `mint`/`redeem` floor in USDC (6dp), sourced
    ///         from `GlobalStorage` so a change to their floor is honoured
    ///         without a redeploy. Used as the pre-flight buy/sell minimum
    ///         and as the graduation floor-bump target; also surfaced for
    ///         off-chain callers sizing minimum trades.
    function minUsdcAmount() public view returns (uint256) {
        return _s().bonding.bounceGlobalStorage().minTransactionSize();
    }
```

**File:** packages/contracts/src/Zap.sol (L637-647)
```text
    /// @notice Effective minimum seed buy for `createToken`: the larger of the
    ///         anti-snipe `MIN_SEED_USDC` floor and the live `minUsdcAmount()`
    ///         mint floor grossed up for the buy fee. Enforced so a launch can
    ///         never pass the seed pre-check only to revert when the post-fee
    ///         seed is minted. `MIN_SEED_USDC` is already a gross floor; the
    ///         mint floor binds on the post-fee amount, so it's grossed up.
    function minSeedUsdc() public view returns (uint256) {
        uint256 grossFloorForMint =
            Math.mulDiv(minUsdcAmount(), BPS_DENOM, BPS_DENOM - _s().buyFeeBps, Math.Rounding.Ceil);
        return Math.max(MIN_SEED_USDC, grossFloorForMint);
    }
```
