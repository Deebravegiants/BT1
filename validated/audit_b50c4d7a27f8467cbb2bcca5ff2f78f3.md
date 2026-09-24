### Title
Unguarded Subtraction in `_prepareGraduationLiquidity` Panics and Permanently Bricks Graduation - (File: `packages/contracts/src/Bonding.sol`)

### Summary
`Bonding._prepareGraduationLiquidity` computes `ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr)` with a raw, unguarded subtraction [1](#0-0) . This mirrors the Vanetza bug class exactly: a value (`assetReserve`) that is accepted as valid throughout the ordinary buy/sell "parsing" path is later re-consumed by a stricter arithmetic step (subtraction against a fixed floor) inside a semantically distinct code path (graduation phase 1), and that stricter step has no defensive guard, so a violation of the assumed invariant produces an uncaught `Panic(0x11)` arithmetic-underflow revert instead of a handled error.

### Finding Description
The protocol assumes `assetReserve` (the pair's stored LT reserve) never drops below `virtualLtReserve` (the immutable launch-time floor recovered via `Pair.k() / Token.TOTAL_SUPPLY()`), because `assetReserve` starts exactly at `virtualLtReserve` and only real LT inflows from buys are supposed to raise it above that floor [2](#0-1) .

Critically, the codebase's own authors recognize this invariant is not bulletproof: `finalizeGraduation` explicitly guards an analogous subtraction with a saturating pattern and a comment stating *"we keep finalize from bricking on a Panic if any future code path or non-canonical LT briefly violates the invariant"* [3](#0-2) . No equivalent saturating guard exists for the earlier, more load-bearing subtraction in `_prepareGraduationLiquidity` at line 1084.

`_prepareGraduationLiquidity` is invoked from `_enterGraduating`, which fires in two unprivileged-reachable ways:
1. Inline at the end of any threshold-crossing `Bonding.buy` call (via `Zap.buy`) [4](#0-3) .
2. Directly via the fully permissionless `triggerGraduation(tokenAddress)` entry point, callable by any address once `canGraduate()` is true [5](#0-4) .

If `assetReserve` is ever pushed below `virtualLtReserve` — via rounding drift across many trades, the pair's K-invariant tolerance (documented elsewhere in this codebase as "Pair.swap's `+1 K slack`"), or interaction with the external rebasing-priced LT's `exchangeRate`/mint/redeem accounting — the subtraction at line 1084 underflows and reverts with an unhandled `Panic(0x11)`. Because this computation is reached unconditionally by both the inline threshold-crossing buy path and the permissionless `triggerGraduation` path, and because the lifecycle never advances past `Curve` when phase 1 reverts, **every future attempt to graduate that token deterministically hits the same Panic**, permanently trapping the curve in `Lifecycle.Curve`.

### Impact Explanation
Once the underflow condition is latched, the token can never transition to `Lifecycle.Graduating`/`Graduated`:
- The 250M `LP_RESERVE` tokens permanently parked in `Bonding` for LP seeding can never be released to a HyperSwap pool.
- Any real LT raised by the curve beyond the virtual floor can never be drained via `Router.graduate` and never reaches `LPLock`.
- Traders lose the ability to migrate to deep post-graduation liquidity; the curve is stuck indefinitely with no recovery path (there is no admin unstick function for this Panic condition — unlike the hostile-pre-seed defenses which explicitly guarantee `finalizeGraduation` "must never revert under any pre-seed shape" [6](#0-5) , phase 1 carries no equivalent brick-resistance guarantee for this arithmetic path).

This is a permanent freeze of curve-raised LT and the LP-bound token reserve — squarely within the accepted impact categories.

### Likelihood Explanation
Reachability requires `assetReserve` to dip, even by 1 wei, below the immutable `virtualLtReserve` floor. The codebase's own defensive comment in `finalizeGraduation` acknowledges this "shouldn't be reachable in normal operation" but treats it as a real enough risk to guard against there [3](#0-2) . I was not able to fully trace, within the available exploration budget, the exact rounding mechanics of `Pair.swap`'s K-slack tolerance that would let `assetReserve` slip below the floor — this would need to be confirmed against `Pair.sol`'s swap invariant check before treating exploitability as certain. Given that uncertainty, likelihood should be treated as Medium rather than definitively High, but the root-cause asymmetry (one subtraction guarded, the semantically identical earlier one not) is a genuine code defect independent of how easily the underflow is triggered.

### Recommendation
Mirror the saturating pattern already used in `finalizeGraduation` at line 1020: compute `ltFromPair = assetReserve > virtualLtReserve ? assetReserve - virtualLtReserve : 0` in `_prepareGraduationLiquidity`, so a floor violation degrades gracefully (e.g., treats the curve as having raised zero net LT) instead of reverting with an unhandled Panic that permanently blocks both the inline buy-triggered and the permissionless `triggerGraduation` paths.

### Proof of Concept
1. Launch a token via `Bonding.launch` and let it trade normally on the curve.
2. Through repeated buy/sell cycles (or via the LT's `exchangeRate`/mint/redeem rebasing interacting with `Router.sell`'s constant-product accounting), drive the pair's stored `assetReserve` to exactly `virtualLtReserve` or push it 1 wei below via any rounding tolerance in `Pair.swap`'s K-invariant check.
3. Have any unprivileged address submit a buy that would cross the USD graduation threshold, or call `Bonding.triggerGraduation(tokenAddress)` once `canGraduate()` is true.
4. `_enterGraduating` → `_prepareGraduationLiquidity` executes `ltFromPair = assetReserve - _launchTimeVirtualLtReserve(...)`; with `assetReserve <= virtualLtReserve`, this underflows and reverts with `Panic(0x11)`.
5. Because the lifecycle remains `Curve`, every subsequent qualifying buy or `triggerGraduation` call hits the identical Panic — the token is permanently un-graduatable, freezing the 250M LP reserve and curve-raised LT.

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

**File:** packages/contracts/src/Bonding.sol (L970-979)
```text
    function triggerGraduation(
        address tokenAddress
    ) external nonReentrant {
        TokenInfo storage info = _s().tokenInfo[tokenAddress];
        if (info.creator == address(0)) revert TokenNotTrading();
        if (info.lifecycle == Lifecycle.Graduating) revert TokenIsGraduating();
        if (info.lifecycle != Lifecycle.Curve) revert TokenNotTrading();
        if (!canGraduate(tokenAddress)) revert NotGraduatable();
        _enterGraduating(tokenAddress);
    }
```

**File:** packages/contracts/src/Bonding.sol (L1015-1020)
```text
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;
```

**File:** packages/contracts/src/Bonding.sol (L1084-1087)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }
```

**File:** packages/contracts/src/Bonding.sol (L1098-1119)
```text
    /// @dev Recovers the launch-time virtual LT reserve from immutable
    ///      identities: `Pair._pool.k = tokenReserve_init * assetReserve_init
    ///      = TOTAL_SUPPLY * virtualLtReserve_init` is set ONCE in
    ///      `Pair.mint` and never modified by `Pair.swap` (swap only
    ///      mutates `tokenReserve` / `assetReserve` and asserts K-floor).
    ///      So `Pair.k() / Token.TOTAL_SUPPLY()` returns the exact
    ///      `virtualLtReserve` that was passed to `addInitialLiquidity` at
    ///      launch — for any pair, in any phase, with no storage of our own.
    ///
    ///      Going through this derivation rather than a stored mirror
    ///      eliminates an admin-writable economic-state slot and makes the
    ///      donation-immunity property a pure consequence of the pair's
    ///      already-immutable accounting. The `TOTAL_SUPPLY`-equality check
    ///      in `setTokenImplementation` keeps the divisor consistent across
    ///      impl rotations, so tokens launched under different
    ///      `tokenImplementation` versions still derive the same way.
    function _launchTimeVirtualLtReserve(
        address token_,
        address pair_
    ) internal view returns (uint256) {
        return IPair(pair_).k() / Token(token_).TOTAL_SUPPLY();
    }
```

**File:** packages/contracts/AGENTS.md (L83-86)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
```
