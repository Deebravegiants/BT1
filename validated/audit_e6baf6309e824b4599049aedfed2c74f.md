Based on my investigation, I found a plausible analog rooted in the same "unchecked integer arithmetic in bonding-curve math causing DoS" bug class as CVE-2024-57640's `dc_add_int` overflow, but I want to flag upfront that I was **not able to fully trace whether `canGraduate`'s underflow-prone expression is inlined into the hot `Bonding.buy`/`sell` path** before running out of tool iterations — this is the load-bearing assumption for severity and needs verification before acting on it.

### Title
Repeated round-trip buys/sells can drift `Pair.assetReserve` below the virtual LT floor, underflowing `Bonding.canGraduate`'s unguarded USD-trigger subtraction and permanently DoS-ing the curve - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Router._computeBuy`/`_computeSell` round `tokensOut`/`assetOut` in the trader's favor by less than 1 wei per trade, and `Pair.swap`'s `+1` K-invariant slack [1](#0-0)  deliberately tolerates the resulting sub-wei drift below the exact constant-product `k`. Over many attacker-driven round trips this drift is monotonically favorable to the trader and can push `assetReserve` below `_launchTimeVirtualLtReserve`, the value subtracted from it — unguarded — in `canGraduate`.

### Finding Description
`canGraduate` computes the USD-trigger leg as: [2](#0-1) 

Unlike `previewLtUntilGraduation`, which explicitly guards the *supply*-leg subtraction against donation-inflated values (`if (realBalance >= reserveToken) return ltUntilThreshold;` [3](#0-2) ), `canGraduate`'s `assetReserve - _launchTimeVirtualLtReserve(token_, pair)` subtraction at line 692 has **no equivalent floor guard**. `_prepareGraduationLiquidity`'s `ltFromPair = storedAssetReserve - virtualLtReserve` computation shares the same unguarded shape per the graduation docs [4](#0-3) .

`Router._computeBuy`/`_computeSell` derive outputs via floor division of `k` by the new reserve [5](#0-4) , which over-delivers to the trader by less than 1 wei per call — the exact tolerance `Pair.swap`'s `(newTokenReserve + 1) * (newAssetReserve + 1) < k` check is built to admit [6](#0-5) . A trader who repeatedly buys a small amount and immediately sells it back extracts this sub-wei favorable rounding on `assetReserve` each round trip, at the cost of gas only (both `buy` and `sell` are permissionless, unprivileged entry points). Given enough repetitions, `assetReserve` can be driven to sit below `_launchTimeVirtualLtReserve(token_, pair)` (the value recovered via `Pair.k() / Token.TOTAL_SUPPLY()`, which never changes post-mint per AGENTS.md's K-identity note), causing `assetReserve - _launchTimeVirtualLtReserve(...)` to underflow and revert on any subsequent read.

### Impact Explanation
If this subtraction is inlined into the buy/sell hot path (the graduation trigger is described as firing "inline by the threshold-crossing buy" per AGENTS.md), every future `Bonding.buy`/`sell` call against the token would revert, permanently freezing the curve: traders can no longer trade, the token can never graduate, and any LT/tokens already committed to the curve are permanently stuck (`Bonding`/`Pair` have no rescue path documented anywhere in this codebase). This satisfies the "permanent freezing of trader/creator funds" bar from the validation criteria — but only if `canGraduate`'s exact expression (or an equivalent) sits in that hot path, which I could not confirm before running out of iterations.

### Likelihood Explanation
The attack requires only gas (no capital risk, since round-trip buy+sell should return principal minus this codebase's Zap/Bonding fees) and a large but bounded number of repetitions bounded by how close `assetReserve` starts to `_launchTimeVirtualLtReserve` — likely on the order of the wei-gap between them, which could be very large for a well-funded seed but small for a freshly-launched, thinly-traded token. This makes it more attractive against low-liquidity, freshly launched tokens.

### Recommendation
Add an explicit floor guard to `canGraduate` (and any other unguarded caller of `assetReserve - _launchTimeVirtualLtReserve(...)`, notably `_prepareGraduationLiquidity`) mirroring the one already present in `previewLtUntilGraduation`: if `assetReserve <= _launchTimeVirtualLtReserve(token_, pair)`, treat the USD leg as not-yet-triggered rather than performing the subtraction unchecked. Separately, verify (and if needed tighten) whether repeated round-trip rounding can actually accumulate past 1 wei-scale noise given the `+1` K-slack's design intent, since the slack was apparently designed to be inert but this asymmetric guard suggests the underflow case was considered solved only for the supply leg, not the USD leg.

### Proof of Concept
Not independently reproduced against the test suite due to tool budget exhaustion. A concrete PoC would: (1) launch a token with a small seed, (2) have an unprivileged trader loop `Bonding.buy` (tiny amount) → `Bonding.sell` (received tokens) via `Zap`/`Bonding` directly, (3) after each iteration read `IPair(pair).getReserves()` and confirm `assetReserve` monotonically decreases by ≤1 wei net of fees, (4) continue until `assetReserve <= Pair.k()/Token.TOTAL_SUPPLY()`, then (5) call `Bonding.canGraduate(token)` or trigger the equivalent inline check in `buy`/`sell` and confirm it reverts with an arithmetic underflow/panic. This should be validated with `test/Bonding.t.sol` / `test/GraduationInvariants.t.sol` harnesses, which already contain analogous donation-drift fixtures (`_stageDonationAttack`) that could be adapted to a round-trip-rounding fixture instead of a token donation.

**Caveat:** given the codebase's extensive, already-tested defenses against structurally similar donation/rounding-underflow issues (the guarded supply leg, the `OverflowCapDegenerate` guard, the brick-resistance test suite), it is possible this exact path is already covered by an inlined check I did not locate, or that the accumulated drift is provably bounded below any realistic gap. I was not able to confirm either way within the available tool budget — this should be verified against `Bonding.sol`'s full `buy`/`sell`/`_enterGraduating` implementation and `test/GraduationInvariants.t.sol` before treating this as confirmed rather than a plausible analog.

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L688-694)
```text
        address pair = info.pair;
        if (IPair(pair).tokenBalance() == 0) return true;

        (, uint256 assetReserve) = IPair(pair).getReserves();
        uint256 realLtRaised = assetReserve - _launchTimeVirtualLtReserve(token_, pair);
        uint256 valueUsd = (realLtRaised * IBounceLeveragedToken(info.ltAddress).exchangeRate()) / 1e18;
        return valueUsd >= $.graduationThresholdUsd;
```

**File:** packages/contracts/src/Bonding.sol (L728-729)
```text
        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;
```

**File:** packages/contracts/AGENTS.md (L89-89)
```markdown
- **Zero-gap LP seeding.** `_prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` (the real LT raised by the curve, donation-immune; `virtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`) and `tokensForLP = ltFromPair × storedTokenReserve / storedAssetReserve` at end-of-phase-1, caching the result. Phase 2 uses the cached value verbatim, so the curve→LP price match is invariant under the tx split. Donated LT stays in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation.
```

**File:** packages/contracts/src/Router.sol (L127-182)
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

    /// @notice Tokens in → LT out.
    function sell(
        uint256 amountIn,
        address token,
        address to
    ) external onlyRole(BONDING_ROLE) returns (uint256 tokensIn, uint256 assetOut) {
        if (amountIn == 0) revert ZeroAmount();

        address asset = assetTokenFor(token);
        address pairAddr = factory.getPair(token, asset);
        if (pairAddr == address(0)) revert PairNotFound();
        tokensIn = amountIn;

        IERC20(token).safeTransferFrom(to, pairAddr, amountIn);

        assetOut = _computeSell(pairAddr, amountIn);

        IPair(pairAddr).transferAsset(to, assetOut);

        IPair(pairAddr).swap(amountIn, 0, 0, assetOut);
    }

    function _computeSell(
        address pairAddr,
        uint256 amountIn
    ) internal view returns (uint256 assetOut) {
        IPair pair = IPair(pairAddr);
        (uint256 reserveToken, uint256 reserveAsset) = pair.getReserves();
        uint256 k = pair.k();

        uint256 newReserveToken = reserveToken + amountIn;
        assetOut = reserveAsset - (k / newReserveToken);
    }
```
