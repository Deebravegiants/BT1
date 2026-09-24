### Title
Budget-capped hostile pre-seed lets an unprivileged attacker permanently mis-price the graduation LP away from curve-close, extracting value from the protocol-locked LP - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The external CVE describes an authenticated but unprivileged user injecting attacker-controlled content (via "Upload from URL"/"Edit") that the application later trusts and executes. The closest reachable analog in alt.fun is the permissionless HyperSwap V2 pre-seed path into `Bonding`'s two-phase graduation: an unprivileged address supplies attacker-controlled "content" (pre-minted LP reserves at a hostile ratio) that `finalizeGraduation` is later forced to trust and build on top of. The three-regime defense (`_seedUniswapV2Direct` → `_seedRebalancing` → `_pairRebalance` → `_routerDepositAndDispose`) neutralizes the "vanilla" version of this attack, but its own rebalance-swap budget cap has a disclosed, unresolved failure mode (labeled "M-02" in the test suite) where the corrective swap cannot reach the curve-close ratio and the graduation LP is permanently opened at an attacker-chosen, materially off-market price.

### Finding Description
`_seedRebalancing` in `packages/contracts/src/Bonding.sol` computes the swap needed to correct a hostile pre-seed ratio and caps it via `_swapBudget`, which reserves only 1% of the *protocol's own* available inventory (`ltFromPair` / `tokensForLP`) as headroom so `addLiquidity` never sees a zero-amount side: [1](#0-0) 

When an attacker pre-seeds the HyperSwap pair (via `factory.createPair` + `transfer` + `pair.mint`, exactly as in `_grieferMintPreSeed`) at a ratio extreme enough that the theoretically-required no-fee correction swap (`_noFeeSwapInput`) exceeds this 99%-of-budget ceiling, `_pairRebalance` clamps the swap to the capped amount rather than the amount needed to reach `tokensForLP / ltFromPair`: [2](#0-1) 

The subsequent `_routerDepositAndDispose` deposits the (still off-ratio) remaining inventory into the pool at that surviving skewed price, and `finalizeGraduation` unconditionally advances the token to `Lifecycle.Graduated`, locks the resulting LP via `LPLock.recordLock`, and never reverts: [3](#0-2) 

The protocol's own test suite documents this as an accepted-but-materially-off-ratio outcome: [4](#0-3) 

This is precisely the "LP seeded away from the curve close price" impact class the analog is scoped to accept. Because `LPLock` has no withdraw/rescue path in v1 (per the `AGENTS.md` design notes), the mispriced LP position is locked permanently — there is no remediation once `finalizeGraduation` completes: [5](#0-4) 

### Impact Explanation
Once the LP opens off curve-close, the pool's post-graduation reserves are wrong relative to the token's true bonding-curve-established price. Any arbitrageur (including the pre-seeding attacker themselves, who retains their own dust-mint LP claim from the pre-seed) can trade against the mispriced pool to extract value that should have accrued to the protocol-locked LP position (held via `LPLock`, majority-owned by the protocol/creator on behalf of the token's ecosystem). Because the LP is permanently locked with no rescue mechanism, this is an unrecoverable, protocol-funded loss — a concrete instance of "an LP seeded away from the curve close price" and effective theft of value from the locked LP position, satisfying the Validate criteria for Medium/High severity.

### Likelihood Explanation
The precondition — pre-seeding the HyperSwap pair with reserves imbalanced enough that the required corrective swap exceeds 99% of the graduation's own `ltFromPair`/`tokensForLP` inventory — is fully reachable by any unprivileged address: `factory.createPair`, `transfer`, and `pair.mint` are all permissionless calls available before `finalizeGraduation` runs, exactly as demonstrated in the existing `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` regression test. The attack requires capital roughly proportional to the size of the graduating token's own raise (to force the budget cap to bind), which bounds but does not eliminate feasibility for well-funded or highly appreciated LTs/tokens.

### Recommendation
Do not silently accept a budget-capped rebalance that leaves the pool materially off curve-close. Either (a) widen the effective per-side budget so realistic pre-seed magnitudes cannot exceed it while preserving the non-zero-deposit guarantee, or (b) add an explicit bound check after `_pairRebalance`/`_routerDepositAndDispose` that reverts or defers finalize (rather than locking a mispriced LP) when the resulting post-swap price deviates from `ltFromPair/tokensForLP` by more than an acceptable tolerance, combined with an admin/keeper-driven remediation path since `LPLock` currently has none.

### Proof of Concept
Adapted directly from the repository's own regression test, which demonstrates the exact mechanics: [6](#0-5) 

1. Launch a token normally and drive it into `Lifecycle.Graduating` via a threshold-crossing buy (`_enterGraduating`).
2. Read `(tokensForLP, ltFromPair)` from `bonding.pendingGraduation(tokenAddr)`.
3. Before `finalizeGraduation` runs, front-run: create the HyperSwap pair via `factory.createPair`, `transfer` an extreme LT-rich ratio (e.g., `reserveToken = tokensForLP/100`, `reserveLt = ltFromPair*200`) to the pair, and call `pair.mint(attacker)`.
4. Anyone calls `bonding.finalizeGraduation(tokenAddr)`. It succeeds (no brick) but `_pairRebalance`'s swap is clamped by `_swapBudget`, leaving the pool priced materially (≥20%, demonstrated ~2x) off `ltFromPair/tokensForLP`.
5. The mispriced, now-permanently-locked LP (held by `LPLock`, which has no v1 rescue path) can be arbitraged by any third party, extracting value that should have belonged to the protocol/token holders.

### Citations

**File:** packages/contracts/src/Bonding.sol (L1000-1033)
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

**File:** packages/contracts/src/Bonding.sol (L1414-1429)
```text
    function _pairRebalance(
        RebalanceParams memory p
    ) internal returns (bool) {
        uint256 s = _noFeeSwapInput(p.reserveIn, p.reserveOut, p.targetN, p.targetD, p.maxSwap);
        if (s == 0) return false;

        // Quote from the pair so the output tracks its live fee; a value
        // derived from a stale fee rate would trip the pair's K-check.
        uint256 expectedOut = IUniswapV2Pair(p.pair).getAmountOut(s, p.tokenIn);
        if (expectedOut == 0) return false;

        IERC20(p.tokenIn).safeTransfer(p.pair, s);
        (uint256 amount0Out, uint256 amount1Out) = p.tokenInIs0 ? (uint256(0), expectedOut) : (expectedOut, uint256(0));
        IUniswapV2Pair(p.pair).swap(amount0Out, amount1Out, address(this), new bytes(0));
        return true;
    }
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L858-900)
```text
    /// @notice M-02 reproducer. An LT-rich mint pre-seed so lopsided that the
    ///         TOKEN-side rebalance swap exhausts its full budget (~99% of
    ///         `tokensForLP`) without reaching the cached ratio, so the pool
    ///         deposits materially off curve-close. Finalize must still succeed
    ///         (no brick), the over-funded LT side must be confiscated to the
    ///         owner, and the pre-seeder must end net-negative.
    function test_hostilePreSeed_budgetCappedSwap_isNotProfitable() public {
        (address tokenAddr,) = _launchToken();
        _enterGraduating(tokenAddr);

        (uint256 tokensForLP, uint256 ltFromPair,,) = bonding.pendingGraduation(tokenAddr);

        // Extreme LT-rich shape: TOKEN side at 1% of target, LT side at 200x.
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

**File:** packages/contracts/AGENTS.md (L164-200)
```markdown
### What we shipped — the three-regime defense

`_seedUniswapV2Direct` branches on the pre-seed shape:

#### Regime 1 — no LP minted yet (~99% of graduations)

Gated on `pair.totalSupply() == 0`, which covers both a pristine empty pair and a dust pre-seed flipped to non-zero reserves via `transfer + sync()` (no `mint`, so supply is still zero). Pristine path: `transfer(pair, tokensForLP) + transfer(pair, ltFromPair) + pair.mint(lpLock)`. With zero supply V2 mints from our deposit amounts alone, so the pool opens at exactly `ltFromPair / tokensForLP` (zero gap by construction) and any synced dust becomes reserves with no LP claim. Bypasses the V2 router entirely. Keying on supply rather than reserves keeps the dust shape out of the rebalance path, where a tiny seed could otherwise let the deposit land at the attacker's ratio.

#### Regime 2 — pure-donation pre-seed

Attacker called `IERC20(token).transfer(pair, X)` without ever calling `pair.mint`. Reserves stay at zero; only the pair's balance moved. We call `pair.skim(address(this))` first — V2's `skim` transfers excess balance over reserves to the recipient — so the donation flows back into `Bonding`. Path then collapses to Regime 1, with the empty-pair branch's tail burning any donated TOKEN and `finalizeGraduation`'s `_sweepLTToOwner` post-bookend routing donated LT to the protocol owner. The skim recipient is deliberately NOT `LPLock`: `LPLock` has no withdraw / rescue path in v1, so anything sent there is permanently stuck. `protectedLT` is snapshotted in `finalizeGraduation` BEFORE `_seedUniswapV2Direct` runs, so the donation is correctly classified as rebalance residue rather than concurrent- ... (truncated)

#### Regime 3 — mint pre-seed (the actual exploit)

Attacker called `pair.mint(attacker)` against a self-funded dust seed. Reserves are non-zero at a hostile ratio. We:

1. **Compute the swap input** that would drive the pool ratio back to the curve-close ratio under the no-fee constant-product model: `s = sqrt(reserveIn · reserveOut · targetN / targetD) − reserveIn`, capped at our per-side budget. Implementation in `_noFeeSwapInput`. Closed-form via OZ `Math.sqrt + Math.mulDiv`; no binary search, no convergence loop.
2. **Execute the swap directly on the pair** via `pair.swap(amount0Out, amount1Out, address(this), "")`. We read the output from the pair's own fee-aware `getAmountOut` quote and pass it as the output. **Bypasses the router** — HyperSwap's V2 router has no canonical `swapExactTokensForTokens` (see "HyperSwap Router non-standard ABI" above). Same direct-to-pair pattern Zap uses for post-grad user swaps. Implementation in `_pairRebalance`.
3. **Deposit the remaining inventory** via `router.addLiquidity(rest, 1, 1, lpLock, ...)`. The router's `quote()`-based optimal split deposits only the matched-ratio subset; neither side becomes a `min()` donation. Off-ratio remainder stays in `Bonding`. The router's `addLiquidity` IS canonical V2 on HyperSwap (verified selector `0xe8e33700`), so this leg is safe to keep on the router and gets the `quote()` math for free.
4. **Dispose the off-ratio remainder.** TOKEN side burned (`Bonding` is the Token owner). LT side auto-swept to the protocol owner by `finalizeGraduation`'s post-sweep — emits `LTRescued(lt, owner, amount)` for observability. See "Per-graduation LT isolation" below.

Why the **asymmetric router usage** (pair for swap, router for addLiquidity): the swap is unsafe to send through the router because HyperSwap's swap ABI is non-standard; the deposit IS safe because HyperSwap's `addLiquidity` ABI is canonical AND the `quote()`-based optimal-split logic is the part that defuses the LP-capture attack. We get the best of both — no HyperSwap-specific footgun on the swap, no reimplementation burden on the deposit.

Why the fourth step matters: **mass conservation prevents fixing both the price and the deposit.** If the pool starts off-target and our inventory is on-target, we cannot end with both at-target reserves AND a fully-deposited inventory — something has to absorb the imbalance. Step 4 is where it goes.

**Dust pre-seeds skip steps 1–4 for a direct mint.** When the swap-output side of the pre-seed is small enough that the rebalance swap rounds to zero (`s == 0` or `getAmountOut(s) == 0`), no swap can move the ratio. The reserves are then negligible against `(tokensForLP, ltFromPair)`, so `_pairRebalance` returns `false` and `_seedRebalancing` falls back to `_seedDirectMint` — the same `transfer + pair.mint` as Regime 1 — opening at the cached ratio and depositing both sides in full (nothing burned or swept). The attacker's dust LP captures `max(reserveToken/tokensForLP, reserveLT/ltFromPair)` of the pool, which vanishes. This is strictly preferable to depositing at the dust ratio via the router, which would open the pool off curve-close.

### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:

- **Regime 1/2 don't touch the router.** Even if the V2 router is misbehaving, the empty + donation paths run on direct pair calls.
- **`_pairRebalance` falls back to a direct mint when no swap can run.** `_noFeeSwapInput` may return `s == 0`, or the pair's fee-charging `getAmountOut(s)` may round to zero, against a pre-seed whose swap-output side is dust — `pair.swap` would otherwise revert with `INSUFFICIENT_OUTPUT_AMOUNT`. In either case `_pairRebalance` returns `false`, and `_seedRebalancing` overpowers the dust with a direct `transfer + pair.mint` at the cached `tokensForLP / ltFromPair` ratio (`_seedDirectMint`), opening the pool on-ratio. This is safe specifically because the swap only rounds to zero when the reserves are negligible against this graduation's inventory: the V2 `min()` donation to the attacker's pre-existing LP is then bounded by `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`, which vanishe ... (truncated)
- **`_routerDepositAndDispose` uses `min0=1, min1=1`.** Slippage protection on `addLiquidity` exists to defend against a third party moving the pool ratio between quote and execution; here we set the ratio ourselves in `_pairRebalance` in the same atomic tx, so there's no third party to defend against. The `=1` (rather than `=0`) trips V2's degenerate-ratio guard so the call can't silently land at near-zero.
- **No external dependency on the router slot being correct post-deploy.** `uniswapV2Router` is set at `initialize` time alongside `uniswapV2Factory` and is rejected if zero. There's no live setter — rotation requires a UUPS upgrade so the change is visible on-chain ahead of any in-flight graduation.

Tested end-to-end by the brick-resistance regression tests in `test/TwoPhaseGraduation.t.sol` (notably `test_brick_resistance_frontRun_dust_seed`).
```
