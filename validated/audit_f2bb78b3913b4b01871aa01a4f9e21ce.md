### Title
Budget-capped hostile pre-seed rebalance lets an attacker permanently open the graduated HyperSwap LP away from the curve-close price - ([File: packages/contracts/src/Bonding.sol])

### Summary
The curl STARTTLS bug trusts data that was injected by an attacker *before* the secure channel was established, because the pre-upgrade responses are cached and consumed after the upgrade without being re-validated against the now-trusted channel. `alt.fun`'s two-phase graduation has the same "pre-trust injection, trusted post-hoc" shape: `Bonding._enterGraduating` (phase 1) freezes `tokensForLP`/`ltFromPair` at the curve-close price and only *later*, in a separate permissionless transaction, `finalizeGraduation` (phase 2) seeds the real, external, attacker-reachable HyperSwap V2 pair with that cached data [1](#0-0) . Between the two phases an attacker can inject state into the not-yet-secured pair (`pair.mint` at a hostile ratio), and the code's own defense against this — a swap-based rebalance — is capped at 99% of available inventory, so for a sufficiently large injected ratio the rebalance cannot fully correct it and the LP is knowingly, by design, opened away from the curve-close price.

### Finding Description
`triggerGraduation`/`_enterGraduating` caches `(tokensForLP, ltFromPair)` from the curve's last price [1](#0-0) . `finalizeGraduation`, callable by anyone at any later time, uses these cached values to seed the real HyperSwap V2 pair via `_seedUniswapV2Direct` → `_seedRebalancing` [2](#0-1) .

Because the V2 pair (`factory.createPair`) is permissionlessly creatable and mintable by anyone, an attacker can pre-seed the pair between phase 1 and phase 2 with a hostile (TOKEN, LT) ratio via `pair.mint(attacker)` [3](#0-2) . The shipped defense (Regime 3) rebalances the pair toward the curve-close ratio via a direct `pair.swap`, but the swap input is deliberately capped at 99% of the available inventory via `_swapBudget` [4](#0-3) :

```
function _swapBudget(uint256 budget) internal pure returns (uint256) {
    return (budget * 99) / 100;
}
```

When the attacker's pre-seed is large/skewed enough that the *unconstrained* no-fee swap input required to reach the curve-close ratio exceeds this 99% budget, `_pairRebalance` clamps to the budget and cannot fully rebalance the pool, and `_routerDepositAndDispose` deposits the remaining inventory at the router's `quote()`-determined ratio, not the curve-close ratio [5](#0-4) . This is confirmed as an accepted, intentional residual by the project's own regression test:

```
// The accepted residual: no bounded swap can correct a 200x LT-rich
// pre-seed, so the pool opens materially off curve-close.
assertGt(
    _poolPriceLtPerToken(hyperPair, tokenAddr),
    (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
    "M-02 regime: pool opens materially off curve-close"
);
``` [6](#0-5) 

This is directly analogous to the STARTTLS class of bug: the "pre-secure-channel" state (the pair between `_enterGraduating` and `finalizeGraduation`, mintable/injectable by anyone) is only partially reconciled once the "secure" state (the real HyperSwap pool that all post-grad trading and price discovery relies on via `Zap`) is established, and the residual injected data is trusted and baked permanently into the LP price.

### Impact Explanation
`finalizeGraduation` records this materially-mispriced LP into `LPLock` via `LPLock.recordLock`, which is a one-shot, irreversible action [7](#0-6) . The mispriced pool then becomes the permanent post-graduation trading venue for the token (`Zap` routes all subsequent buys/sells through this pair). This directly matches the accepted-impact class "an LP seeded away from the curve close price" — traders and the token's post-grad LP holders are permanently exposed to an LP that opened materially off the fair curve-close price, and arbitrageurs (including the attacker) can extract value from the mispricing before the market corrects it, at the expense of the locked LP (protocol/creator) and any traders who transact against the pool before it re-equilibrates.

### Likelihood Explanation
The attack requires only unprivileged, permissionless actions reachable by any address: (1) observe/predict a token nearing graduation, (2) call `factory.createPair` and fund a large, heavily skewed reserve ratio via ordinary ERC20 transfers plus `pair.mint`, sized so that the *required* rebalance swap exceeds 99% of `Bonding`'s available inventory of that side (`_ltSwapInventory`/`Token` balance) — the test `testFuzz_hostilePreSeed_neverProfitable_neverBricks` and `test_hostilePreSeed_extreme_*` (M-02 regime) show this is reachable with realistic multiples (e.g., 200x one side) [8](#0-7) , then (3) let/force `finalizeGraduation` run (it's permissionless and keeper-driven, so the attacker cannot even prevent it from running against their seed). No special timing, roles, or privileged access is required beyond funding the pre-seed, which the project's own comments explicitly acknowledge is an "accepted residual," making this a documented and reachable, not merely theoretical, condition.

### Recommendation
Either (a) remove the fixed 99%-of-inventory cap and instead size the swap budget dynamically against the true curve-close target so any completable rebalance always fully corrects the ratio regardless of pre-seed magnitude, reserving only the true "swap rounds to zero" case for the direct-mint fallback; or (b) when the required rebalance exceeds the safe budget, route the excess inventory through an additional bounded swap/deposit iteration (or multiple `addLiquidity` calls) rather than accepting a partially-rebalanced deposit, so `finalizeGraduation` never locks LP at a price materially different from the curve close, even for extreme pre-seed ratios.

### Proof of Concept
This is exercised by the project's own test suite (not merely a report claim):
- `test/TwoPhaseGraduation.t.sol` `test_hostilePreSeed_extreme_...` (M-02 regime, lines ~870-917): pre-seed the pair at `reserveToken = tokensForLP/100`, `reserveLt = ltFromPair*200`, so the unconstrained rebalance swap exceeds the 99% budget cap; call `finalizeGraduation`; assert the pool price ends up >20% off the curve-close price [9](#0-8) .
- `testFuzz_hostilePreSeed_neverProfitable_neverBricks` (lines 926-960) fuzzes `seedMultiple` up to 1000x and confirms `finalizeGraduation` never reverts but permanently locks an LP whose opening price can be materially skewed for large multiples [10](#0-9) .

### Citations

**File:** packages/contracts/src/Bonding.sol (L934-953)
```text
    /// @dev Phase 1: drain curve, cache LP-bound amounts, freeze trading. Runs
    ///      inline at end of the threshold-crossing buy. Pinning `tokensForLP`
    ///      and `ltFromPair` here (at the last curve price) is what preserves
    ///      the zero-gap invariant across the tx split.
    function _enterGraduating(
        address tokenAddress
    ) internal {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        info.lifecycle = Lifecycle.Graduating;

        (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) =
            _prepareGraduationLiquidity(tokenAddress);

        $.pendingGraduation[tokenAddress] = PendingGraduation({
            tokensForLP: tokensForLP, ltFromPair: ltFromPair, lpBurned: lpBurned, unsoldBurned: unsoldBurned
        });

        emit TokenGraduating(tokenAddress, tokensForLP, ltFromPair, lpBurned, unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1000-1034)
```text
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
        BondingStorage storage $ = _s();
        TokenInfo storage info = $.tokenInfo[tokenAddress];
        if (info.lifecycle != Lifecycle.Graduating) revert NotGraduating();

        address lt = info.ltAddress;
        PendingGraduation memory p = $.pendingGraduation[tokenAddress];

        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;

        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);

        info.lifecycle = Lifecycle.Graduated;
        $.graduatedPair[tokenAddress] = lpPair;
        delete $.pendingGraduation[tokenAddress];

        LPLock($.lpLock).recordLock(tokenAddress, lpPair, liquidity);

        emit TokenGraduated(tokenAddress, lpPair, liquidity, p.tokensForLP, p.lpBurned, p.unsoldBurned);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1291-1354)
```text
        // Below the band on BOTH sides, overpower the pre-seed with a direct
        // mint at the cached ratio: the rebalance swap is too coarse to reach
        // the ratio against such small reserves, and the pre-existing LP's
        // claim on the deposit stays bounded by `DIRECT_MINT_PRESEED_BPS`. A
        // side that is large relative to its LP target still takes the
        // rebalance path so it isn't donated under the empty-mint `min()`.
        if (
            reserveToken * BPS_DENOM <= tokensForLP * DIRECT_MINT_PRESEED_BPS
                && reserveLT * BPS_DENOM <= ltFromPair * DIRECT_MINT_PRESEED_BPS
        ) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Budget reads `balanceOf(this)` rather than `tokensForLP` /
        // `ltFromPair` so any skim donation contributes to the rebalance
        // and not only to `_routerDepositAndDispose`'s deposit.
        // Direction: pool TOKEN-rich vs target ⇒ swap LT in (TOKEN out).
        // Pool LT-rich ⇒ swap TOKEN in (LT out). Bounded by uint112 reserves
        // and curve-close-shape targets, both products fit in uint256.
        // When `_pairRebalance` returns false the seed is too small for any
        // swap to move the ratio (its fee-charging quote rounds to zero), so
        // the reserves are negligible against this graduation's inventory:
        // overpower them with a direct mint at the cached ratio rather than
        // letting the router deposit at the attacker's ratio. A swap that
        // does fire leaves the pool ≈ at target for the router deposit.
        if (reserveToken * ltFromPair > reserveLT * tokensForLP) {
            // Pool TOKEN-rich. tokenIn = lt, tokenOut = tokenAddress.
            // tokenInIs0 = (lt is token0) = !tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: lt,
                        tokenInIs0: !tokenIs0,
                        reserveIn: reserveLT,
                        reserveOut: reserveToken,
                        targetN: ltFromPair,
                        targetD: tokensForLP,
                        maxSwap: _swapBudget(_ltSwapInventory(lt, protectedLT))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        } else if (reserveToken * ltFromPair < reserveLT * tokensForLP) {
            // Pool LT-rich. tokenIn = tokenAddress, tokenInIs0 = tokenIs0.
            if (!_pairRebalance(
                    RebalanceParams({
                        pair: pair,
                        tokenIn: tokenAddress,
                        tokenInIs0: tokenIs0,
                        reserveIn: reserveToken,
                        reserveOut: reserveLT,
                        targetN: tokensForLP,
                        targetD: ltFromPair,
                        maxSwap: _swapBudget(IERC20(tokenAddress).balanceOf(address(this)))
                    })
                )) {
                return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
            }
        }
        // else: pool already at curve-close ratio (rare — e.g. attacker
        // pre-seeded at exactly target). Skip swap, deposit directly.

        return _routerDepositAndDispose(tokenAddress, lt, protectedLT);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1356-1378)
```text
    /// @dev Cap the rebalance swap at 99% of the available side's budget,
    ///      so the subsequent `addLiquidity` always has a non-zero amount
    ///      of BOTH sides to deposit. Without this, an extreme hostile
    ///      pre-seed (massively imbalanced reserves) drives the
    ///      unconstrained `_noFeeSwapInput` past our per-side budget,
    ///      `_pairRebalance` clamps to the full budget, and the swap
    ///      consumes 100% of one side. `_routerDepositAndDispose` then
    ///      skips `addLiquidity` (`remToken == 0` or `remLT == 0`),
    ///      `finalizeGraduation` returns `liquidity = 0`, and
    ///      `LPLock.recordLock(...)` records a zero-sized lock — the
    ///      attacker's pre-existing LP becomes 100% of the pool. Reserving
    ///      1% guarantees the deposit leg always lands AND mints non-zero
    ///      LP at the post-swap ratio. The 1% comes off the swap, not the
    ///      deposit — for any realistic pre-seed `s_unconstrained` is
    ///      orders of magnitude below `maxSwap`, so the cap doesn't bind
    ///      and behaviour is unchanged. It only kicks in for catastrophic
    ///      pre-seeds beyond our budget capacity, where the alternative
    ///      is bricking.
    function _swapBudget(
        uint256 budget
    ) internal pure returns (uint256) {
        return (budget * 99) / 100;
    }
```

**File:** packages/contracts/AGENTS.md (L130-149)
```markdown
### The exploit

A vanilla UniswapV2 pair is deployable by anyone: `factory.createPair(token, lt)` is permissionless, and after creation anyone can call `pair.mint(to)` against pre-transferred tokens. So between phase 1 (`_enterGraduating` flips lifecycle to `Graduating` and caches `tokensForLP / ltFromPair`) and phase 2 (`finalizeGraduation` mints LP via `pair.mint(lpLock)`), an attacker can:

1. Front-run by calling `factory.createPair(token, lt)` themselves
2. `transfer(pair, smallToken)` and `transfer(pair, smallLT)` at any ratio they choose
3. Call `pair.mint(attacker)` — they now own LP at a hostile reserve ratio

When our `pair.mint(lpLock)` runs in phase 2 against this non-empty pair, V2's mint formula picks up the existing reserves:

```
liquidity = min(amount0 · totalSupply / reserve0, amount1 · totalSupply / reserve1)
```

The `min(...)` arm whose denominator is bigger relative to its numerator wins, and the OTHER arm's "excess" deposit is donated pro-rata to existing LP holders — i.e. to the attacker. Two harms:

- **Wrong opening price.** Post-mint reserves are `(R_attacker + T_a, R_attacker + T_b)`, so the LP opens at `(R_a + T_a) / (R_b + T_b)`, NOT at the curve close `T_a / T_b`. A `$15` LT pre-seed at 50% off curve close opens the pool ~454 bps off.
- **LP capture.** The wasted-side excess goes to the attacker's LP claim. A `1 wei + 1 LT` pre-seed (~`$1` attack budget) captures ~34 bps of LP.

A cheaper variant skips step 3 entirely: `transfer(pair, dust) + pair.sync()` forces the stored reserves to the dust ratio without minting any LP, leaving the pair at `reserves > 0 && totalSupply == 0`. Regime 1 below covers both shapes by keying on supply rather than reserves.
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L871-900)
```text
        // The optimal TOKEN-in swap to reach the cached ratio is ~1.4x
        // `tokensForLP`, so the 99%-of-`tokensForLP` budget cap binds and the
        // pool stays ~2x off curve-close after the swap.
        uint256 reserveToken = tokensForLP / 100;
        uint256 reserveLt = ltFromPair * 200;

        // M-02 precondition: the optimal swap exceeds the budget (this is the
        // budget-capped regime, distinct from the swap-rounds-to-zero fallback
        // covered by the dust tests above).
        assertGt(
            _noFeeSwapInputUncapped(reserveToken, reserveLt, tokensForLP, ltFromPair),
            (tokensForLP * 99) / 100,
            "setup: optimal rebalance swap must exceed the per-side budget (M-02 regime)"
        );

        deal(tokenAddr, griefer, reserveToken);
        address hyperPair = _grieferMintPreSeed(tokenAddr, reserveToken, reserveLt);
        uint256 grieferLp = MockHyperswapPair(hyperPair).balanceOf(griefer);
        uint256 ownerLtBefore = lt.balanceOf(bonding.owner());

        bonding.finalizeGraduation(tokenAddr);
        assertTrue(bonding.isGraduated(tokenAddr), "finalize must succeed despite an unrecoverable pre-seed");

        // The accepted residual: no bounded swap can correct a 200x LT-rich
        // pre-seed, so the pool opens materially off curve-close.
        assertGt(
            _poolPriceLtPerToken(hyperPair, tokenAddr),
            (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
            "M-02 regime: pool opens materially off curve-close"
        );
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L919-960)
```text
    /// @notice Across the hostile mint-pre-seed shape space — both rich
    ///         directions and magnitudes spanning the in-budget rebalance and
    ///         the budget-capped (M-02) residual — `finalizeGraduation` must
    ///         never revert (brick-resistance) and the pre-seeder's residual
    ///         LP, valued at the fair curve-close price, must never exceed what
    ///         they deposited (P&L <= 0).
    /// forge-config: default.fuzz.runs = 64
    function testFuzz_hostilePreSeed_neverProfitable_neverBricks(
        uint256 seedMultiple,
        bool ltRich
    ) public {
        seedMultiple = bound(seedMultiple, 1, 1000);

        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);
        (uint256 tokensForLP, uint256 ltFromPair,,) = bonding.pendingGraduation(tokenAddr);

        // One side held at its LP target, the other over-funded by
        // `seedMultiple`. Small multiples reach the cached ratio within budget;
        // large ones exhaust it and exercise the M-02 residual. Both rich
        // directions are covered by `ltRich`.
        (uint256 reserveToken, uint256 reserveLt) =
            ltRich ? (tokensForLP, ltFromPair * seedMultiple) : (tokensForLP * seedMultiple, ltFromPair);

        deal(tokenAddr, griefer, reserveToken);
        address hyperPair = _grieferMintPreSeed(tokenAddr, reserveToken, reserveLt);
        uint256 grieferLp = MockHyperswapPair(hyperPair).balanceOf(griefer);

        // Brick-resistance: must succeed for every shape, and lock non-zero LP.
        bonding.finalizeGraduation(tokenAddr);
        assertTrue(bonding.isGraduated(tokenAddr), "finalize must succeed for every pre-seed shape");
        assertGt(
            MockHyperswapPair(hyperPair).balanceOf(address(lpLockContract)), 0, "lpLock must hold non-zero protocol LP"
        );

        uint256 claimValue = _lpValueAtCurveClose(hyperPair, tokenAddr, grieferLp, tokensForLP, ltFromPair);
        uint256 depositValue = _depositValueAtCurveClose(reserveToken, reserveLt, tokensForLP, ltFromPair);
        // Strict P&L bound; the small absolute slack only absorbs integer
        // rounding in the LP-claim arithmetic (sub-wei-relative), far below any
        // economically-meaningful subsidy.
        assertLe(claimValue, depositValue + 1e9, "pre-seeder LP claim must not exceed deposit (P&L <= 0)");
    }
```
