### Title
Permissionless HyperSwap pre-seed can force `finalizeGraduation` to open the graduated LP materially off the bonding-curve close price - (File: `packages/contracts/src/Bonding.sol`)

### Summary
The Vim CVE's shape is: a setting that should be trusted/secure (`path`) can instead be populated from attacker-controlled content (a file's modeline) and is later consumed, unchecked, by a routine user action (`:find` completion), producing attacker-directed behavior. The structural analog in `alt.fun` is `Bonding._seedUniswapV2Direct`'s "Regime 3" mint-pre-seed handling: the HyperSwap V2 TOKEN/LT pair's reserve ratio is attacker-settable before `finalizeGraduation` runs (a permissionless, routine action), and the rebalance defense that is supposed to correct that ratio is bounded by a fixed per-side budget. When an attacker seeds a sufficiently extreme ratio, the budget cap binds, the corrective swap cannot fully repair the ratio, and the pool is deposited — via the routine `finalizeGraduation` call — at a price materially different from the curve's close price.

### Finding Description
`Bonding.finalizeGraduation` (phase 2 of the two-phase graduation) seeds liquidity into a HyperSwap V2 pair using `_prepareGraduationLiquidity`'s cached `(tokensForLP, ltFromPair)` values, computed at phase-1 time to match the curve's close price [1](#0-0) .

Because HyperSwap V2 pairs are permissionlessly creatable and mintable, an attacker can front-run the pair (`factory.createPair` + `transfer` + `pair.mint(attacker)`) to set the pool's initial reserve ratio to anything, before `finalizeGraduation` is ever called [2](#0-1) . The protocol's defense (`_seedUniswapV2Direct` Regime 3) attempts to rebalance this hostile ratio back toward the curve-close ratio via a direct `pair.swap`, using a closed-form no-fee swap-input formula (`_noFeeSwapInput`) that is explicitly capped at a fixed per-side budget [3](#0-2) .

When the pre-seed ratio is extreme enough that the mathematically optimal rebalancing swap would exceed this budget, the cap binds and the swap only partially corrects the ratio — the remaining inventory is then deposited via `router.addLiquidity` at the still-skewed ratio, and any leftover LT is confiscated to the owner rather than restoring the price [4](#0-3) . This exact regime is reproduced and asserted in the test suite: an LT-rich pre-seed (`reserveToken = tokensForLP/100`, `reserveLt = ltFromPair*200`) causes the optimal correcting swap to exceed 99% of `tokensForLP`, so after `finalizeGraduation` the resulting pool price is proven to be at least 1.2x off the curve-close price [5](#0-4) .

The parallel to the Vim CVE is direct: the "setting" here is the HyperSwap pair's reserve ratio — a state variable that the graduation logic implicitly trusts to be correctable within its fixed swap budget, but which lacks any hard validation/guard analogous to Vim's missing `P_SECURE` flag. An unprivileged attacker sets this state ahead of time (the modeline-equivalent), and it is consumed unchecked by the routine, permissionless `finalizeGraduation` call (the `:find`-completion-equivalent trigger), producing an outcome (a mispriced LP) that the protocol did not intend.

### Impact Explanation
The outcome is a graduated LP opened at a price materially different from the bonding curve's close price — an explicitly listed acceptable-impact class ("an LP seeded away from the curve close price"). This distorts the market price new post-graduation traders see, creates an arbitrage opportunity against the protocol's own locked LP, and permanently locks the mispriced liquidity via `LPLock` (no withdraw path in v1) [6](#0-5) .

### Likelihood Explanation
The trigger requires only permissionless, unprivileged-address actions: `factory.createPair`, `IERC20.transfer` to the pair, and `pair.mint(attacker)` — all reachable by any wallet before `finalizeGraduation` runs, exactly as the test's `_grieferMintPreSeed` helper demonstrates [7](#0-6) . `finalizeGraduation` itself is also permissionless, so nothing prevents the attacker (or anyone) from completing the sequence in one attacker-controlled window.

### Recommendation
Since the developers already treat this as a known, accepted residual (the "M-02" comment naming), the concrete mitigation would be to widen the rebalance budget dynamically based on how far off-ratio the pre-seed is (rather than a fixed percentage of `tokensForLP`), or to detect budget-capped scenarios and fall back to a mechanism that guarantees the price gap stays within a hard bound (e.g., iteratively re-seeding via multiple swap+deposit rounds, or bounding LP mint size to the un-skewed inventory and burning/holding the remainder rather than depositing at a bad ratio).

### Proof of Concept
The existing regression test is a working PoC: [8](#0-7) 
It stages `reserveToken = tokensForLP/100` and `reserveLt = ltFromPair*200` via `_grieferMintPreSeed`, calls `bonding.finalizeGraduation(tokenAddr)`, and asserts the resulting pool price is `>= 1.2×` the curve-close price — proving the LP is seeded away from the curve close price through purely permissionless calls.

### Citations

**File:** packages/contracts/AGENTS.md (L83-91)
```markdown
- **Two-phase split.** Graduation is split across two transactions to fit HyperEVM's small-block (~2M gas) ceiling.
  - **Phase 1: `_enterGraduating`**, fired inline by the threshold-crossing buy (~150-200k of additional gas on top of the buy). Drains the curve, computes the LP-bound amounts, caches them in `pendingGraduation[token]`, flips `lifecycle: Curve → Graduating`, freezes trading. Emits `TokenGraduating`.
  - **Phase 2: `finalizeGraduation`**, **permissionless** big-block tx (~2.5M gas). Creates the HyperSwap pair if needed, seeds liquidity across the empty, donation, and hostile mint-pre-seed regimes, locks LP, flips `lifecycle: Graduating → Graduated`. Emits `TokenGraduated`. A Cloudflare Worker keeper handles the happy path; anyone can call to rescue a stuck token.
- **Brick resistance.** Phase 2 must never revert under any pre-seed shape. Empty/donation pairs use direct pair calls; hostile mint pre-seeds use direct `pair.swap` for rebalance plus router `addLiquidity` for the canonical quote-based deposit. Tested by `test_brick_resistance_frontRun_dust_seed` in [`test/TwoPhaseGraduation.t.sol`](test/TwoPhaseGraduation.t.sol).
- **Virtual token reserve.** At launch, `Pair.reserve0 = totalSupply (1B)` while only `curveSupply = 75%` (750M) of real tokens are transferred to the pair. The other 250M (`LP_RESERVE`) sit in `Bonding` for graduation. This extends the curve beyond the sellable supply, which is what makes dynamic LP seeding work cleanly.
- **Dual trigger.** Phase 1 fires on whichever hits first: `(storedAssetReserve - virtualLtReserve) × exchangeRate ≥ $9K` (USD, for LT pumps) or `IPair.tokenBalance() == 0` (supply, for flat/bear markets). The USD trigger reads STORED reserves so direct LT donations to the pair don't count toward the threshold; the launch-time `virtualLtReserve` is recovered on-the-fly as `Pair.k() / Token.TOTAL_SUPPLY()` (K is set once at mint and never modified by `Pair.swap`). The supply trigger reads live `tokenBalance()`, which is donation-resistant in the opposite direction: token donations only INCREASE the balance and can never satisfy `== 0`, and any donated tokens are unconditionally burned by `_prepareGraduationLiquidity`.
- **Zero-gap LP seeding.** `_prepareGraduationLiquidity` computes `ltFromPair = storedAssetReserve - virtualLtReserve` (the real LT raised by the curve, donation-immune; `virtualLtReserve` is derived from `Pair.k() / Token.TOTAL_SUPPLY()`) and `tokensForLP = ltFromPair × storedTokenReserve / storedAssetReserve` at end-of-phase-1, caching the result. Phase 2 uses the cached value verbatim, so the curve→LP price match is invariant under the tx split. Donated LT stays in the curve pair under the trust assumption that `BONDING_ROLE` is only ever held by `Bonding` and `Bonding` won't call `Router.graduate` again post-graduation.
- **Parabola invariant.** With `V_t_init = totalSupply` and `curveSupply = 75%`, the function `tokensForLP(sold) = sold·(S−sold)/S` peaks at `S/4 = LP_RESERVE`. The cap in `_prepareGraduationLiquidity` is defensive — it can never bind in normal operation.
- **Overflow buy cap.** `Router.buy` caps `tokensOut` at the pair's real balance and back-calculates the LT consumed, so the last buy cannot exceed remaining supply. `Zap.buy` returns the unused LT (`ltMinted - amountInUsed`) directly as LT — not redeemed, to avoid re-incurring the LT redemption fee on dust — while unconverted USDC and the fee over-charge are refunded in USDC. `Bonding.buy` returns `(tokensOut, amountInUsed)` for this reason.
```

**File:** packages/contracts/AGENTS.md (L130-150)
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

**File:** packages/contracts/AGENTS.md (L151-151)
```markdown
This is the same exploit class as the four.meme Feb 2025 incident (~$183K loss).
```

**File:** packages/contracts/AGENTS.md (L185-197)
```markdown
Why the **asymmetric router usage** (pair for swap, router for addLiquidity): the swap is unsafe to send through the router because HyperSwap's swap ABI is non-standard; the deposit IS safe because HyperSwap's `addLiquidity` ABI is canonical AND the `quote()`-based optimal-split logic is the part that defuses the LP-capture attack. We get the best of both — no HyperSwap-specific footgun on the swap, no reimplementation burden on the deposit.

Why the fourth step matters: **mass conservation prevents fixing both the price and the deposit.** If the pool starts off-target and our inventory is on-target, we cannot end with both at-target reserves AND a fully-deposited inventory — something has to absorb the imbalance. Step 4 is where it goes.

**Dust pre-seeds skip steps 1–4 for a direct mint.** When the swap-output side of the pre-seed is small enough that the rebalance swap rounds to zero (`s == 0` or `getAmountOut(s) == 0`), no swap can move the ratio. The reserves are then negligible against `(tokensForLP, ltFromPair)`, so `_pairRebalance` returns `false` and `_seedRebalancing` falls back to `_seedDirectMint` — the same `transfer + pair.mint` as Regime 1 — opening at the cached ratio and depositing both sides in full (nothing burned or swept). The attacker's dust LP captures `max(reserveToken/tokensForLP, reserveLT/ltFromPair)` of the pool, which vanishes. This is strictly preferable to depositing at the dust ratio via the router, which would open the pool off curve-close.

### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:

- **Regime 1/2 don't touch the router.** Even if the V2 router is misbehaving, the empty + donation paths run on direct pair calls.
- **`_pairRebalance` falls back to a direct mint when no swap can run.** `_noFeeSwapInput` may return `s == 0`, or the pair's fee-charging `getAmountOut(s)` may round to zero, against a pre-seed whose swap-output side is dust — `pair.swap` would otherwise revert with `INSUFFICIENT_OUTPUT_AMOUNT`. In either case `_pairRebalance` returns `false`, and `_seedRebalancing` overpowers the dust with a direct `transfer + pair.mint` at the cached `tokensForLP / ltFromPair` ratio (`_seedDirectMint`), opening the pool on-ratio. This is safe specifically because the swap only rounds to zero when the reserves are negligible against this graduation's inventory: the V2 `min()` donation to the attacker's pre-existing LP is then bounded by `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`, which vanishe ... (truncated)
- **`_routerDepositAndDispose` uses `min0=1, min1=1`.** Slippage protection on `addLiquidity` exists to defend against a third party moving the pool ratio between quote and execution; here we set the ratio ourselves in `_pairRebalance` in the same atomic tx, so there's no third party to defend against. The `=1` (rather than `=0`) trips V2's degenerate-ratio guard so the call can't silently land at near-zero.
```

**File:** packages/contracts/src/Bonding.sol (L1155-1183)
```text
    ///        3. **Mint pre-seed.** Attacker called `pair.mint` against a
    ///           self-funded seed, baking a hostile (TOKEN, LT) ratio into
    ///           the pool. Without intervention `pair.mint(lpLock)`'s
    ///           `min(amount0·S/r0, amount1·S/r1)` formula would (a) open
    ///           the LP off curve-close-price and (b) donate the larger arm
    ///           to the attacker's pre-existing LP. We rebalance via a
    ///           direct `pair.swap` toward the curve-close ratio, then
    ///           deposit the remaining inventory via the router's
    ///           `quote()`-based `addLiquidity` — which only pulls the
    ///           optimal amounts at the post-swap ratio, so neither side
    ///           becomes a `min()` donation. Off-ratio TOKEN remainder is
    ///           burned; off-ratio LT remainder is auto-swept to the owner
    ///           by `finalizeGraduation`'s post-bookend (see its natspec).
    ///           When the seed is small enough that the fee-charging swap
    ///           quote rounds to zero, no swap can move the ratio — but the
    ///           reserves are then negligible against this graduation's
    ///           inventory, so we fall back to the regime-1 direct mint
    ///           (`_seedDirectMint`) and open at the cached ratio anyway.
    ///           The captured LP share is bounded by
    ///           `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`,
    ///           which vanishes for any seed that small.
    ///
    ///      Brick resistance: the rebalance swap input is capped at our
    ///      per-side budget; a swap whose fee-charging `getAmountOut` would
    ///      round to zero (which would otherwise revert `pair.swap` with
    ///      `INSUFFICIENT_OUTPUT_AMOUNT`) is replaced by the direct-mint
    ///      fallback; the deposit uses `addLiquidity(min=1, min=1)`; and the
    ///      empty/donation regimes don't touch the router or `pair.swap`. So
    ///      a hostile pre-seed of any shape cannot DoS `finalizeGraduation`.
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L499-510)
```text
    /// @dev Front-run the pair: create it, fund both reserves at the given
    ///      (hostile) ratio, and mint dust LP to the griefer.
    function _grieferMintPreSeed(
        address tokenAddr,
        uint256 reserveTokenAmt,
        uint256 reserveLtAmt
    ) internal returns (address hyperPair) {
        require(Token(tokenAddr).balanceOf(griefer) >= reserveTokenAmt, "test setup: griefer short on tokens");
        MockHyperswapFactory hsFactory = MockHyperswapFactory(hyperswapRouter.factory());
        hyperPair = hsFactory.createPair(tokenAddr, address(lt));
        lt.mintDirect(griefer, reserveLtAmt);
        vm.startPrank(griefer);
```

**File:** packages/contracts/test/TwoPhaseGraduation.t.sol (L858-917)
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

        // The over-funded LT side is arbed out by the rebalance swap and swept
        // to the owner — the pre-seeder cannot recover it.
        assertGt(
            lt.balanceOf(bonding.owner()) - ownerLtBefore,
            reserveLt / 2,
            "the over-funded LT side must be confiscated to the owner"
        );

        // P&L: the pre-seeder's residual LP, valued at the fair (curve-close)
        // price, is worth a fraction of what they deposited — the attack is
        // cost-negative.
        uint256 claimValue = _lpValueAtCurveClose(hyperPair, tokenAddr, grieferLp, tokensForLP, ltFromPair);
        uint256 depositValue = _depositValueAtCurveClose(reserveToken, reserveLt, tokensForLP, ltFromPair);
        assertLe(claimValue, depositValue, "pre-seeder must not profit (P&L <= 0)");
        assertLt(claimValue * 2, depositValue, "pre-seeder must lose materially, not merely break even");
    }
```
