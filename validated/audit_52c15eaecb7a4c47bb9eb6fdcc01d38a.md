### Title
Cross-Graduation LT Isolation Bypass in Hostile-Preseed Rebalance Swap Budget - ([File: packages/contracts/src/Bonding.sol])

### Summary
`Bonding.finalizeGraduation` computes `protectedLT = balanceOf(this) - p.ltFromPair` specifically to wall off LT belonging to a *concurrent* graduation on the same LT (or stray dust) from being consumed by the current graduation's LP seeding [1](#0-0) . This isolation is documented as load-bearing precisely because two tokens sharing one LT can both be `Graduating` simultaneously [2](#0-1) . However, in the hostile-mint-preseed rebalance path (`_seedRebalancing` → `_pairRebalance`), the swap budget is explicitly sized off `IERC20(lt).balanceOf(this)` rather than the graduation's own cached `ltFromPair`, by the code's own admission: "Budget reads `balanceOf(this)` rather than `tokensForLP` / `ltFromPair` so any skim donation contributes to the rebalance" [3](#0-2) . This is the exact same class of bug as CVE-2021-3283 (Nomad exec/java task drivers reaching into another task's isolated resources): an operation scoped to "this graduation" is allowed to touch state (here, LT balance) that is supposed to be quarantined for a different, concurrent principal (a different token's escrowed graduation LT).

### Finding Description
`finalizeGraduation` snapshots `protectedLT` up front and threads it through `_seedUniswapV2Direct` → `_seedRebalancing` → `_routerDepositAndDispose`, where the *deposit* leg is correctly capped at `balanceOf(this) - protectedLT` [4](#0-3) . But the rebalance *swap* budget computed inside `_seedRebalancing`/`_pairRebalance` (the `maxSwap` field of `RebalanceParams`) is derived from the raw `balanceOf(this)` of the LT side, not `balanceOf(this) - protectedLT` [5](#0-4) . The comment only rationalizes this in terms of a same-graduation skim donation ("any skim donation contributes to the rebalance"), but a concurrent graduation's already-escrowed `ltFromPair` (moved into `Bonding` by `Router.graduate` during that token's own Phase 1, per `_prepareGraduationLiquidity`) is indistinguishable from a donation at this point in the code [6](#0-5) . When token A's `finalizeGraduation` lands in the Regime-3 hostile-preseed branch and the pool is LT-rich relative to A's target ratio, `_pairRebalance` will swap LT into the pair using a budget sized against the full contract-wide LT balance — which can include token B's protected escrow if B is concurrently `Graduating` on the same LT.

### Impact Explanation
If the rebalance swap consumes LT beyond token A's own `ltFromPair_A`, it draws down token B's escrowed `ltFromPair_B` that was supposed to remain untouched until B's own `finalizeGraduation` runs. Concretely:
- Token B's later `finalizeGraduation` call computes its own `protectedLT`/deposit against a now-depleted `balanceOf(this)`, so `_seedDirectMint`/`_routerDepositAndDispose` either transfers less LT than `ltFromPair_B` to B's pool (opening B's LP at a wrong, non-curve-close price — a documented "zero-gap" invariant violation) or reverts/underflows depending on downstream arithmetic, effectively freezing B's graduation.
- The LT that left B's escrow is spent as swap input for A's rebalance and ends up disposed of via `_routerDepositAndDispose`'s off-ratio sweep/burn or locked in A's LP — i.e., value that belonged to B's raisers/creator/traders is transferred into A's graduation outcome.

This is concrete freezing/misallocation of LT funds across two unrelated, permissionless token launches sharing an LT, triggerable by any unprivileged party who arranges (or opportunistically exploits) a hostile mint pre-seed on a concurrently-graduating pair — a scenario the protocol's own AGENTS.md flags as realistic ("popular LTs see overlap") [7](#0-6) .

### Likelihood Explanation
`finalizeGraduation` is permissionless [8](#0-7) , and mint pre-seeding a not-yet-graduated pair is directly reachable by any wallet via `IUniswapV2Pair.mint` before `finalizeGraduation` executes, per the protocol's own hostile-preseed defense design [9](#0-8) . The precondition (two tokens on the same LT both reaching `Graduating` before either finalizes) is explicitly acknowledged as an occurring scenario, not a theoretical edge case, and the dedicated regression suite for these exact isolation properties (`test/HostilePreSeed.t.sol`) was removed post-deployment and is no longer enforced by automated tests [10](#0-9) .

### Recommendation
Size the rebalance `maxSwap` budget off `balanceOf(this) - protectedLT` (mirroring the deposit-leg cap in `_routerDepositAndDispose`) rather than raw `balanceOf(this)`, so a concurrent graduation's escrowed LT can never be consumed as swap input by another token's rebalance. Re-add or rebuild the concurrent-graduation isolation regression coverage that was dropped with `test/HostilePreSeed.t.sol`.

### Proof of Concept
Conceptual sequence (exact numeric parameters require a fork/unit-test harness to confirm the boundary, which is outside static review):
1. Token A and Token B are both launched against the same LT and both independently reach `Lifecycle.Graduating` (each via its own threshold-crossing buy), so `Bonding` now holds `ltFromPair_A + ltFromPair_B` of LT, per Phase 1's `Router.graduate` transfers [11](#0-10) .
2. An unprivileged attacker calls `pair.mint(attacker)` against Token A's not-yet-finalized HyperSwap pair with a self-funded dust seed skewed so the pool is LT-rich relative to A's cached target ratio, forcing Regime 3.
3. Anyone calls `bonding.finalizeGraduation(tokenA)`. `_seedRebalancing`/`_pairRebalance` compute the swap budget from `balanceOf(this)` (which includes B's escrowed `ltFromPair_B`), and the swap consumes more LT than `ltFromPair_A` alone would allow.
4. `bonding.finalizeGraduation(tokenB)` subsequently executes with a depleted LT balance, producing an LP seeded at a skewed price relative to B's true curve-close price, or a shortfall that misallocates B's raised funds.

### Citations

**File:** packages/contracts/src/Bonding.sol (L981-1002)
```text
    /// @notice Phase 2: seed the V2 LP and lock it. Permissionless —
    ///         keeper drives the happy path; anyone can rescue a stuck token.
    /// @dev Bypasses the V2 router and calls `pair.mint(lpLock)`
    ///      directly. This is brick-proof against a front-runner pre-creating
    ///      the pair and dust-seeding it between phases.
    /// @dev Exchange-rate drift between phase 1 and phase 2 is accepted by
    ///      design. The cached `(tokensForLP, ltFromPair)` are pure pair-
    ///      state arithmetic — see `_prepareGraduationLiquidity`, which
    ///      never reads `exchangeRate()` — so the LP opens at the exact
    ///      LT-per-token ratio the curve closed at, regardless of how long
    ///      phase 2 takes. What drifts is only the USD denomination of the
    ///      LT side, which is inherent to using a leveraged token as the
    ///      curve reserve: holders accept that exposure when they buy in.
    ///      A keeper Worker drives finalize within ~60s of `TokenGraduating`,
    ///      so the practical drift window is single-digit seconds. No
    ///      freshness timestamp / staleness gate: a recompute would return
    ///      byte-identical values (inputs are frozen while
    ///      `Lifecycle.Graduating`), and re-pricing the LP at the live
    ///      `exchangeRate()` would break the zero-gap-in-LT-units invariant.
    function finalizeGraduation(
        address tokenAddress
    ) external nonReentrant {
```

**File:** packages/contracts/src/Bonding.sol (L1010-1025)
```text
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
```

**File:** packages/contracts/src/Bonding.sol (L1084-1096)
```text
        ltFromPair = assetReserve - _launchTimeVirtualLtReserve(tokenAddress, pairAddr);
        if (ltFromPair > 0) {
            _s().router.graduate(tokenAddress, ltFromPair);
        }

        tokensForLP = assetReserve == 0 ? 0 : (ltFromPair * tokenReserve) / assetReserve;
        if (tokensForLP > LP_RESERVE) tokensForLP = LP_RESERVE;

        lpBurned = LP_RESERVE - tokensForLP;
        if (lpBurned > 0) {
            Token(tokenAddress).burn(address(this), lpBurned);
        }
    }
```

**File:** packages/contracts/src/Bonding.sol (L1279-1316)
```text
    function _seedRebalancing(
        address tokenAddress,
        address lt,
        address pair,
        uint256 tokensForLP,
        uint256 ltFromPair,
        uint256 protectedLT
    ) internal returns (uint256 liquidity) {
        (uint112 r0, uint112 r1,) = IUniswapV2Pair(pair).getReserves();
        bool tokenIs0 = IUniswapV2Pair(pair).token0() == tokenAddress;
        (uint256 reserveToken, uint256 reserveLT) = tokenIs0 ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));

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
```

**File:** packages/contracts/AGENTS.md (L176-189)
```markdown
#### Regime 3 — mint pre-seed (the actual exploit)

Attacker called `pair.mint(attacker)` against a self-funded dust seed. Reserves are non-zero at a hostile ratio. We:

1. **Compute the swap input** that would drive the pool ratio back to the curve-close ratio under the no-fee constant-product model: `s = sqrt(reserveIn · reserveOut · targetN / targetD) − reserveIn`, capped at our per-side budget. Implementation in `_noFeeSwapInput`. Closed-form via OZ `Math.sqrt + Math.mulDiv`; no binary search, no convergence loop.
2. **Execute the swap directly on the pair** via `pair.swap(amount0Out, amount1Out, address(this), "")`. We read the output from the pair's own fee-aware `getAmountOut` quote and pass it as the output. **Bypasses the router** — HyperSwap's V2 router has no canonical `swapExactTokensForTokens` (see "HyperSwap Router non-standard ABI" above). Same direct-to-pair pattern Zap uses for post-grad user swaps. Implementation in `_pairRebalance`.
3. **Deposit the remaining inventory** via `router.addLiquidity(rest, 1, 1, lpLock, ...)`. The router's `quote()`-based optimal split deposits only the matched-ratio subset; neither side becomes a `min()` donation. Off-ratio remainder stays in `Bonding`. The router's `addLiquidity` IS canonical V2 on HyperSwap (verified selector `0xe8e33700`), so this leg is safe to keep on the router and gets the `quote()` math for free.
4. **Dispose the off-ratio remainder.** TOKEN side burned (`Bonding` is the Token owner). LT side auto-swept to the protocol owner by `finalizeGraduation`'s post-sweep — emits `LTRescued(lt, owner, amount)` for observability. See "Per-graduation LT isolation" below.

Why the **asymmetric router usage** (pair for swap, router for addLiquidity): the swap is unsafe to send through the router because HyperSwap's swap ABI is non-standard; the deposit IS safe because HyperSwap's `addLiquidity` ABI is canonical AND the `quote()`-based optimal-split logic is the part that defuses the LP-capture attack. We get the best of both — no HyperSwap-specific footgun on the swap, no reimplementation burden on the deposit.

Why the fourth step matters: **mass conservation prevents fixing both the price and the deposit.** If the pool starts off-target and our inventory is on-target, we cannot end with both at-target reserves AND a fully-deposited inventory — something has to absorb the imbalance. Step 4 is where it goes.

**Dust pre-seeds skip steps 1–4 for a direct mint.** When the swap-output side of the pre-seed is small enough that the rebalance swap rounds to zero (`s == 0` or `getAmountOut(s) == 0`), no swap can move the ratio. The reserves are then negligible against `(tokensForLP, ltFromPair)`, so `_pairRebalance` returns `false` and `_seedRebalancing` falls back to `_seedDirectMint` — the same `transfer + pair.mint` as Regime 1 — opening at the cached ratio and depositing both sides in full (nothing burned or swept). The attacker's dust LP captures `max(reserveToken/tokensForLP, reserveLT/ltFromPair)` of the pool, which vanishes. This is strictly preferable to depositing at the dust ratio via the router, which would open the pool off curve-close.
```

**File:** packages/contracts/AGENTS.md (L210-221)
```markdown
### Per-graduation LT isolation

`finalizeGraduation` snapshots `protectedLT = balanceOf(this) - p.ltFromPair` at the top: any LT in `Bonding` beyond this graduation's earmark is either another concurrent graduation's escrow (Phase 1 already moved it in via `Router.graduate`) or stray dust. Both must stay out of THIS graduation's LP and post-sweep.

That snapshot is plumbed through `_seedUniswapV2Direct` → `_seedRebalancing` → `_routerDepositAndDispose`, where the deposit allowance is capped at `balanceOf(this) - protectedLT`. Then a single `_sweepLTToOwner(lt, protectedLT)` at the end of `finalizeGraduation` sends only THIS graduation's rebalance residue to the protocol owner, leaving any concurrent-graduation escrow / stray dust untouched. Honest empty-pair graduations have no residue at the post-sweep so it's a no-op there.

Two scenarios this guards against:

- **Concurrent graduations on the same LT.** Two tokens A and B share an LT and both reach `Lifecycle.Graduating` before either finalizes (the keeper takes ~60s and popular LTs see overlap). Without `protectedLT`, A's finalize would treat the full balance as its own and either sweep B's escrow to the owner (bricking B's later finalize) or — for hostile-pre-seed graduations — deposit it into A's locked LP. With it, A only ever sees `ltFromPair_A` and B is preserved.
- **Cross-token LT residue.** Old residue or a misdirected transfer sitting in `Bonding` would otherwise be visible to `_routerDepositAndDispose`'s `balanceOf(this)` read and could be silently consumed into a future graduation's locked LP. With `protectedLT`, contamination stays in `Bonding` and the deposit only sees this graduation's earmark.

The auto-sweep emits `LTRescued(lt, owner, amount)` for indexer observability. The dedicated regression tests for these edge cases were removed alongside `HostilePreSeed.t.sol`; future changes to `finalizeGraduation` / `_routerDepositAndDispose` / `_sweepLTToOwner` should add targeted coverage if the behaviour is non-obvious from the unit-level tests in `TwoPhaseGraduation.t.sol`.
```

**File:** packages/contracts/AGENTS.md (L225-231)
```markdown
- `test/NoFeeSwapInput.t.sol` — 9 deterministic + 2 fuzz tests on the load-bearing math (degenerate inputs, monotonicity, cap-at-budget, closed-form correctness, overflow safety, the round-down-to-zero input shape that motivated the precheck).
- `test/TwoPhaseGraduation.t.sol` — brick-resistance + phase-1-fits-in-small-block tests, plus the hostile-pre-seed open-at-cached-ratio tests (`test_hostilePreSeed_*`) covering both the dust direct-mint fallback and the meaningful-reserve swap path, must still pass.
- `test/GraduationInvariants.t.sol` — zero-gap, supply conservation, parabola cap. Honest-path properties unchanged by the defense.

The dedicated end-to-end hostile-pre-seed integration suite (`test/HostilePreSeed.t.sol`) was removed for runtime reasons after deployment — the wrong-opening-price / LP-capture scenarios, attacker-no-profit, leftover recovery, and concurrent-graduation isolation properties are no longer enforced by automated tests. If you change any of the graduation / rebalance / deposit code paths, consider re-deriving these properties manually and / or adding targeted regressions for whatever you touch.

These invariants are the security contract — do not loosen the remaining assertions to make a change go green.
```
