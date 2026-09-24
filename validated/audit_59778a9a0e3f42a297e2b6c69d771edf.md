### Title
Attacker-sized Token donation permanently bricks Router's overflow-buy cap, freezing curve graduation via the supply trigger - ([File: packages/contracts/src/Router.sol])

### Summary
An unprivileged address can permanently disable the "overflow buy cap" safety branch in `Router._computeBuy` by donating a precisely-sized amount of the launched `Token` directly to its `Pair`. Once the donation drives the pair's real `tokenBalance()` to exactly equal the stored `tokenReserve`, every subsequent buy that is large enough to trigger the cap branch reverts unconditionally with `OverflowCapDegenerate`, and this condition is self-perpetuating across all future ordinary buys. This permanently blocks the only mechanism (`Bonding`'s supply-based graduation trigger) that can graduate a token whose paired LT never appreciates enough to hit the USD trigger, trapping the 250M `LP_RESERVE` and any curve-raised LT for that token forever.

### Finding Description
`Router._computeBuy` caps `tokensOut` at the pair's live ERC20 balance whenever the uncapped curve output would exceed it, then back-derives `amountInUsed` from a degenerate reserve: [1](#0-0) 

The safety of the `cappedReserveToken == 0 → revert OverflowCapDegenerate` branch depends entirely on the invariant `tokenBalance() < tokenReserve()` holding at all times, which the codebase's own test suite documents as being guaranteed only under normal buy operations: [2](#0-1) 

This invariant is explicitly broken by a plain ERC20 donation of `Token` directly into the `Pair` — a path the codebase already anticipates and partially guards elsewhere (`Bonding.previewLtUntilGraduation` special-cases `realBalance >= reserveToken`), but `Router._computeBuy` itself has no such guard: [3](#0-2) 

The project's own regression tests confirm an attacker can cheaply drive `tokenBalance() > tokenReserve()` via a curve drain + donation: [4](#0-3) 

Because `Router.buy` transfers `tokensOut` out of the pair via `pair.transferToken` and then calls `Pair.swap`, which decrements the stored `tokenReserve` by that exact same `tokensOut` for every non-capped buy: [5](#0-4) 

...the gap between `tokenBalance()` and `tokenReserve()` is preserved across every subsequent ordinary buy. If an attacker sizes the donation so that `tokenBalance() == tokenReserve()` exactly (both values are readable via `getReserves()`/`tokenBalance()`), the equality persists indefinitely. Any buy from then on that is large enough to reach the cap branch computes `cappedReserveToken = reserveToken - realBalance = 0` and reverts with `OverflowCapDegenerate` — permanently, since normal buys keep the two values in lockstep rather than closing the gap.

### Impact Explanation
`Bonding`'s dual graduation trigger relies on the supply trigger (`IPair.tokenBalance() == 0`) specifically to cover the case where the LT's exchange rate never rises enough to satisfy the USD trigger — the documented "flat/bear markets" fallback: [6](#0-5) 

Once the cap branch is bricked for a token, no buy can ever fully drain `tokenBalance()` to zero, so a token stuck in a flat/bear LT-price regime can never graduate. This permanently freezes: (a) the 250M `LP_RESERVE` tokens earmarked in `Bonding` for that token's HyperSwap LP seeding, and (b) any real LT raised on the curve, which is only released via `Router.graduate` during `finalizeGraduation` — a code path that is unreachable while the token remains in `Lifecycle.Curve` forever. Smaller buys below the cap-triggering size still succeed, so trading is not fully halted, but the token can never complete graduation, permanently stranding LP-bound funds.

### Likelihood Explanation
The donation primitive needed (buy a large slice of the curve, then `Token.transfer` it to the `Pair`) is already demonstrated as cheap and reachable by an unrelated, unprivileged wallet in the codebase's own donation-attack tests. Precisely hitting `tokenBalance() == tokenReserve()` only requires reading two public view functions (`getReserves()`, `tokenBalance()`) and sending one extra dust transfer to close the remaining gap — well within reach of any trader, and independent of any privileged role.

### Recommendation
Add the same defensive guard used in `Bonding.previewLtUntilGraduation` (donation-inflated `realBalance >= reserveToken` ⇒ treat supply leg as already satisfied / skip the cap-degenerate computation) directly inside `Router._computeBuy`, e.g. treat `realBalance >= reserveToken` as "curve already exhausted" and cap `tokensOut` at `realBalance - 1` (or route straight into the graduation supply trigger) instead of computing a division that can degrade to a permanent revert.

### Proof of Concept
1. Launch a token normally via `Zap.createToken`.
2. As an unrelated attacker wallet, buy on the curve (via `Bonding.buy`/`Zap.buy`) enough to acquire a large `Token` balance — mirroring `_stageDonationAttack` in [7](#0-6) .
3. Read `(reserveToken, _) = Pair.getReserves()` and `realBalance = Pair.tokenBalance()`; `Token.transfer(pair, reserveToken - realBalance)` to close the gap to exact equality.
4. Submit (or wait for) any buy sized to hit `Router._computeBuy`'s cap branch (i.e., large enough that uncapped `tokensOut > realBalance`) — this now always reverts with `OverflowCapDegenerate`, per [8](#0-7) .
5. As long as the paired LT's `exchangeRate()` never independently drives the USD trigger past `graduationThresholdUsd`, the token remains permanently stuck in `Lifecycle.Curve`, with `LP_RESERVE` and raised LT permanently unreleased.

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

**File:** packages/contracts/src/Bonding.sol (L705-736)
```text
    function previewLtUntilGraduation(
        address token_
    ) external view returns (uint256) {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[token_];
        if (info.creator == address(0)) return 0;
        if (info.lifecycle != Lifecycle.Curve) return 0;

        address pair = info.pair;
        uint256 realBalance = IPair(pair).tokenBalance();
        if (realBalance == 0) return 0;

        (uint256 reserveToken, uint256 reserveAsset) = IPair(pair).getReserves();

        uint256 ltUntilThreshold = type(uint256).max;
        uint256 exchangeRate = IBounceLeveragedToken(info.ltAddress).exchangeRate();
        if (exchangeRate > 0) {
            uint256 realLtRaised = reserveAsset - _launchTimeVirtualLtReserve(token_, pair);
            uint256 thresholdRealLt = ($.graduationThresholdUsd * 1e18 + exchangeRate - 1) / exchangeRate;
            if (realLtRaised >= thresholdRealLt) return 0;
            ltUntilThreshold = thresholdRealLt - realLtRaised;
        }

        // Donation-inflated `realBalance`: supply trigger unreachable, defer to USD leg.
        if (realBalance >= reserveToken) return ltUntilThreshold;

        uint256 cappedReserveToken = reserveToken - realBalance;
        uint256 cappedReserveAsset = (IPair(pair).k() + cappedReserveToken - 1) / cappedReserveToken;
        uint256 ltUntilSupply = cappedReserveAsset - reserveAsset;

        return ltUntilSupply < ltUntilThreshold ? ltUntilSupply : ltUntilThreshold;
    }
```

**File:** packages/contracts/test/Zap.t.sol (L944-977)
```text
    function _stageDonationAttack(
        address tokenAddr
    ) internal returns (uint256 drainLtSpent, uint256 donatedTokens) {
        address pairAddr = bonding.getTokenInfo(tokenAddr).pair;
        address drainer = makeAddr("donationDrainer");
        // Size the drain so `tokensOut > 250M` (the LP-reserve floor) under
        // any `VIRTUAL_LIQUIDITY_USD`. Constant-product math gives
        // `tokensOut = TOTAL_SUPPLY × ltIn / (virtual + ltIn)`, which crosses
        // 250M (= ¼ of TOTAL_SUPPLY) when `ltIn = virtual / 3`. Spending the
        // full opening virtual reserve lands `tokensOut = 500M` — plenty of
        // headroom to push `realBalance > reserveToken` after the donation.
        drainLtSpent = _initialVirtualLt();
        lt.mintDirect(drainer, drainLtSpent);
        if (!bonding.isRouter(drainer)) bonding.addRouter(drainer);
        vm.startPrank(drainer);
        lt.approve(address(curveRouter), drainLtSpent);
        bonding.buy(drainLtSpent, tokenAddr, 0, drainer);
        vm.stopPrank();
        donatedTokens = Token(tokenAddr).balanceOf(drainer);
        vm.prank(drainer);
        Token(tokenAddr).transfer(pairAddr, donatedTokens);
    }

    function test_donation_realBalanceExceedsReserveToken() public {
        address tokenAddr = _createToken(0);
        address pairAddr = bonding.getTokenInfo(tokenAddr).pair;

        (, uint256 donated) = _stageDonationAttack(tokenAddr);
        assertGt(donated, 250_000_000 ether, "Drain must yield > 250M tokens to break the gap");

        uint256 realBalance = IPair(pairAddr).tokenBalance();
        (uint256 reserveToken,) = IPair(pairAddr).getReserves();
        assertGt(realBalance, reserveToken);
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

**File:** docs/contracts-scope.md (L66-73)
```markdown
## Graduation

Dual trigger — fires on whichever hits first:

- **USD trigger:** `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (HYPE pumps raise the USD value of already-raised LT above the threshold). Reads the pair's STORED reserves; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` because `_pool.k = totalSupply * virtualLtReserve` is locked in at `Pair.mint` and never modified by swaps.
- **Supply trigger:** `IPair.tokenBalance() == 0` (all 750M curve tokens sold; handles flat/bear markets where $9K is never reached). This IS a live `balanceOf` read but is donation-resistant in the opposite direction — token donations can only INCREASE the balance and can never satisfy `== 0`. Any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.

Direct LT donations to the pair don't count toward the USD threshold and don't enter the LP — they stay in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding`. `Bonding.canGraduate()` is checked at the end of every buy inside `_executeBuy`; phase 1 (`Bonding._enterGraduating`) fires inline at the end of the threshold-crossing buy. There is no rate-only trigger: a USD ripening driven purely by `exchangeRate()` motion (no intervening buy) holds the ripe state only while the rate stays above threshold, and is settled by the next buy that lands while still ripe. The supply trigger is monotonic — once `tokenBalance() == 0` it cannot un-ripen, so the next buy will graduate it. A sell can never satisfy a trigger on its own (it reduces stored LT raised and  ... (truncated)
```
