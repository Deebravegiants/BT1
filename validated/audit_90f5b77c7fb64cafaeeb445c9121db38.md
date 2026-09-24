Based on the codebase's own hostile-pre-seed defense mechanism and its documented residual limitation, there is a valid analog to the CVE's "Protection Mechanism Failure" class: alt.fun's dedicated defense against HyperSwap pre-seeding (`_seedRebalancing` → `_pairRebalance` → `_swapBudget`) is a purpose-built protection mechanism that can be driven to fail under an extreme, but fully attacker-reachable, pre-seed shape, resulting in the graduation LP being seeded materially away from the curve-close price.

### Title
Hostile HyperSwap Pre-Seed Rebalance Defense Fails Under Extreme LT-Rich Pre-Seed, Seeding the Graduation LP Materially Off Curve-Close Price - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding._seedUniswapV2Direct` implements a "Regime 3" defense (`_seedRebalancing`/`_pairRebalance`) whose explicit purpose is to protect the graduation LP from opening at a hostile ratio when an attacker pre-creates the HyperSwap V2 TOKEN/LT pair and mints LP against a self-chosen ratio before `finalizeGraduation` runs. That protection mechanism caps the corrective swap at 99% of the available side's budget (`_swapBudget`). When the pre-seed ratio is extreme enough that the swap required to reach the curve-close ratio exceeds this cap, the rebalance swap only partially corrects the price, and the graduation LP is deposited at a materially off-ratio price instead of the intended zero-gap curve-close price.

### Finding Description
`finalizeGraduation` seeds the graduated HyperSwap V2 pool via `_seedUniswapV2Direct`, which branches into `_seedRebalancing` whenever the pair already has non-trivial pre-existing LP (Regime 3, the "mint pre-seed" attack) [1](#0-0) .

`_seedRebalancing` computes the required corrective swap via `_noFeeSwapInput` and caps it with `_swapBudget`, which reserves only 99% of the relevant side's inventory for the swap:

```
function _swapBudget(uint256 budget) internal pure returns (uint256) {
    return (budget * 99) / 100;
}
``` [2](#0-1) 

The natspec on `_swapBudget` and the surrounding code acknowledges this cap is a defensive floor against bricking, not a guarantee of price correctness: "for any realistic pre-seed `s_unconstrained` is orders of magnitude below `maxSwap`, so the cap doesn't bind and behaviour is unchanged. It only kicks in for catastrophic pre-seeds beyond our budget capacity" [3](#0-2) .

When an attacker pre-seeds the pair with a sufficiently LT-rich ratio (e.g., `reserveLT = 200 × ltFromPair`, `reserveToken = tokensForLP / 100`), the swap required to correct the ratio exceeds the 99%-of-budget cap, so `_pairRebalance` executes a capped, under-sized swap and `_routerDepositAndDispose` deposits the remaining inventory at a pool ratio that is still materially off the curve-close price [4](#0-3) .

The project's own regression test confirms this residual failure mode explicitly (labelled "M-02"):

```
function test_hostilePreSeed_budgetCappedSwap_isNotProfitable() public {
    ...
    assertGt(
        _poolPriceLtPerToken(hyperPair, tokenAddr),
        (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
        "M-02 regime: pool opens materially off curve-close"
    );
``` [5](#0-4) 

This is fully reachable by an unprivileged wallet: `factory.createPair(token, lt)` is permissionless, and `pair.mint(attacker)` is callable by anyone against self-transferred tokens/LT — exactly the flow the protocol's own defense doc describes as "the exploit" and lists as an in-scope, attacker-reachable path [6](#0-5) . `finalizeGraduation` is permissionless and unconditionally proceeds despite the mispriced result, since the brick-resistance property is prioritized over the LP-capture/pricing defense by design [7](#0-6) .

### Impact Explanation
This directly matches the "LP seeded away from the curve close price" impact criterion. The graduation LP — 250M tokens plus the entire curve-raised LT, minted to `LPLock` and majority-owned by the protocol/community on behalf of the graduated token — opens at a price that can diverge by >20% (per the project's own test threshold) from the true curve-close price. Arbitrageurs immediately capture that gap by trading against the mispriced pool, extracting value from the protocol-owned LP position (the party holding ~99% of the post-mint LP), and post-graduation traders (`Zap.buy`/`Zap.sell` against the HyperSwap pool) transact at a materially wrong price immediately after graduation.

### Likelihood Explanation
Requires an attacker to fund a very large, deliberately lopsided pre-seed (order of 100–200× the token's `ltFromPair`) in the paired LT and front-run `finalizeGraduation` — costly in capital, though that capital is largely confiscated to the protocol owner via `_sweepLTToOwner` rather than lost outright to the attacker, so this is not a profitable exploit for the attacker per se. The realistic driver is not attacker profit-seeking but a large, low-effort pre-seed used purely to grief the pool's opening price at the expense of the protocol/graduated-token LP and its earliest post-grad traders. Likelihood is Medium: it's economically irrational for a pure profit-motivated attacker but trivially executable griefing given permissionless `createPair`/`mint`, and the codebase itself explicitly documents and tests this exact residual (not a hypothetical).

### Recommendation
Either (a) increase the corrective-swap budget ceiling (or make it iterative/multi-hop) so it can correct larger pre-seed ratios before falling back to a capped deposit, or (b) when the budget cap binds and the post-swap price remains outside an acceptable tolerance band, fall back to `_seedDirectMint` at the cached curve-close ratio (burning/sweeping the hostile pre-seed's excess, as already done for the dust regime) rather than depositing through the router at a still-mispriced ratio. This preserves brick-resistance while closing the price-gap residual for large pre-seeds.

### Proof of Concept
Reference `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` in `packages/contracts/test/TwoPhaseGraduation.t.sol` (lines 864–900), which already reproduces this end-to-end: launch a token, drive it into `Graduating`, have the `griefer` create the HyperSwap pair and `pair.mint` against `reserveToken = tokensForLP/100` and `reserveLT = ltFromPair*200`, then call `bonding.finalizeGraduation(tokenAddr)`. The assertion `_poolPriceLtPerToken(...) > (ltFromPair*1e18/tokensForLP)*1.2` passes, confirming the pool opens more than 20% off the curve-close price. [8](#0-7)

### Citations

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

**File:** packages/contracts/src/Bonding.sol (L1201-1234)
```text
    function _seedUniswapV2Direct(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        // Regime 2 — pull any donation pre-seed into this contract so it
        // doesn't pollute the post-swap ratio. Routed to `address(this)`
        // (NOT `lpLock`) so donated TOKEN can be burned and donated LT
        // can be swept to the owner via `_sweepLTToOwner` — `LPLock` has
        // no rescue path, so anything sent there is permanently stuck.
        // No-op on a freshly-created pair (balance == reserves == 0).
        IUniswapV2Pair(pair).skim(address(this));

        // Regime 1 — no LP minted yet (`totalSupply == 0`): a pristine empty
        // pair, or a dust pre-seed from `transfer(pair, dust) + sync()` that
        // leaves reserves non-zero while supply is still zero. Keying on
        // supply rather than reserves routes the dust shape here instead of
        // the rebalance path: with zero supply V2 mints from our amounts
        // alone, so the pool opens at the cached ratio and any dust becomes
        // reserves with no LP claim.
        if (IUniswapV2Pair(pair).totalSupply() == 0) {
            return _seedDirectMint(tokenAddress, lt, pair, tokensForLP, ltFromPair);
        }

        // Regime 3 — mint pre-seed: rebalance, then deposit balanced subset.
        // `lpLock_` re-read from storage inside `_routerDepositAndDispose`.
        // Reserves and token-ordering re-read inside `_seedRebalancing` to
        // keep this function's stack pressure under solc's 16-slot ceiling
        // without `viaIR`.
        return _seedRebalancing(tokenAddress, lt, pair, tokensForLP, ltFromPair, protectedLT);
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
