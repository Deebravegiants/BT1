### Title
Budget-capped hostile-mint-preseed rebalance lets a HyperSwap V2 LP seed materially off the bonding-curve close price (M-02) - ([File: packages/contracts/src/Bonding.sol])

### Summary
The OKX report describes fake/mispriced order-book state being shown to traders. The closest on-chain analog in this codebase is `Bonding.sol`'s two-phase graduation LP seeding into HyperSwap V2, where a sufficiently extreme, attacker-funded pre-seed of the `TOKEN/LT` pair can exhaust the rebalance swap's per-side budget and cause `finalizeGraduation` to open the graduated pool at a price materially different from the bonding curve's last traded ("close") price — i.e., traders are shown/get a pool price that misrepresents true curve value, mirroring the "fake displayed price/liquidity" bug class in the report.

### Finding Description
`Bonding._seedUniswapV2Direct` (documented in `packages/contracts/AGENTS.md:126-232` and implemented via `_seedRebalancing` / `_pairRebalance` / `_noFeeSwapInput` / `_routerDepositAndDispose`) defends against a permissionless `factory.createPair` + `transfer` + `pair.mint(attacker)` front-run that would otherwise let an attacker bake a hostile reserve ratio into the pre-graduation pair.

For "Regime 3" (a mint pre-seed with non-trivial reserves), the defense computes a closed-form no-fee swap input `_noFeeSwapInput` to rebalance the pair back toward the cached curve-close ratio (`tokensForLP : ltFromPair`, computed in `_prepareGraduationLiquidity`, `packages/contracts/src/Bonding.sol:1073-1096`), then deposits the remaining inventory via `router.addLiquidity(min=1, min=1)`.

This rebalance swap is explicitly capped at "our per-side budget" (~99% of `tokensForLP`/`ltFromPair`, per `AGENTS.md:180` and the `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` regression). When the pre-seed ratio is extreme enough that the required rebalancing swap exceeds this budget (e.g., an LT-rich pre-seed where LT reserve is ~200x `ltFromPair` against a token reserve at ~1% of `tokensForLP`), the swap cannot fully correct the ratio. `_routerDepositAndDispose` then deposits the remaining inventory at the still-skewed post-swap ratio, and the pool opens roughly 2x off the curve-close price, as demonstrated by `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` in `packages/contracts/test/TwoPhaseGraduation.t.sol:858-917`, which asserts:
```
assertGt(
    _poolPriceLtPerToken(hyperPair, tokenAddr),
    (((ltFromPair * 1e18) / tokensForLP) * 12) / 10,
    "M-02 regime: pool opens materially off curve-close"
);
```
This is a permissionless attack surface: any unrelated address can call `factory.createPair(token, lt)` and `pair.mint(attacker)` between phase 1 (`_enterGraduating`, triggered inline by any trader's threshold-crossing `Bonding.buy`/`Zap.buy`) and phase 2 (`finalizeGraduation`, permissionless), with no allowlist or privileged role required.

### Impact Explanation
The protocol's own locked LP (held in `LPLock`, non-withdrawable in v1) is seeded at a price that diverges materially (~2x demonstrated, unbounded in the worst case) from the bonding curve's true closing price. This directly matches the accepted impact class "an LP seeded away from the curve close price." Traders/LPs interacting with the newly graduated pool see and trade against a mispriced pool until arbitrage (if it occurs) corrects it — arbitrage activity itself extracts value from the protocol-owned LP (locked, non-recoverable), representing a permanent value transfer out of protocol-controlled liquidity. Severity is Medium: it requires an attacker to fund the extreme pre-seed (LT and token inventory) and does not directly enrich the attacker (P&L for the attacker is bounded ≤0 per the existing test), but it does cause the protocol/LP-lock-held liquidity to be mispriced and lose value to arbitrageurs, which is the exact harm class the report/rules call out.

### Likelihood Explanation
Reaching `Lifecycle.Graduating` requires only a normal `Zap.buy` crossing the USD or supply graduation trigger — reachable by any trader. Front-running `finalizeGraduation` with `factory.createPair` + `transfer` + `pair.mint(attacker)` is fully permissionless (HyperSwap V2 pair creation and minting have no access control), and `finalizeGraduation` itself is explicitly permissionless (`AGENTS.md:85`, meant to be callable "to rescue a stuck token"), so an attacker fully controls the timing and shape of the pre-seed within the accepted budget-exceeding parameter space. The main cost/friction is funding the LT and token inventory for the extreme ratio (e.g., ~200x `ltFromPair` in LT), which bounds likelihood to attackers with meaningful capital, but no privileged role or race against a keeper is required to trigger the M-02 residual — only sizing the pre-seed correctly.

### Recommendation
- Tighten or remove the fixed ~99% per-side swap budget cap in `_noFeeSwapInput`/`_pairRebalance`, or make it iterative/multi-hop so extreme ratios can still be corrected without exceeding a single-swap budget, while preserving the brick-resistance guarantee (never revert).
- Alternatively, when the budget-capped regime is detected (ratio cannot be fully corrected), route the excess off-ratio inventory through an additional bounded rebalance pass (or several smaller swaps) before the final `addLiquidity` deposit, rather than depositing directly at the still-skewed ratio.
- Add an explicit monitoring/alert (or a smaller acceptable-deviation assertion enforced on-chain, reverting only when a safe fallback exists) so that any graduation opening more than a fixed bps threshold off curve-close is flagged for manual/keeper remediation before value is arbitraged out of the locked LP.

### Proof of Concept
Existing repository test `test_hostilePreSeed_budgetCappedSwap_isNotProfitable` in `packages/contracts/test/TwoPhaseGraduation.t.sol:864-917` already reproduces this exact scenario end-to-end:
1. Launch a token and drive it into `Lifecycle.Graduating` via `_enterGraduating` (i.e., a normal threshold-crossing buy).
2. Before `finalizeGraduation` is called, an unrelated `griefer` address front-runs by creating the HyperSwap pair, transferring `reserveToken = tokensForLP/100` TOKEN and `reserveLt = ltFromPair*200` LT into it, and calling `pair.mint(griefer)` (via `_grieferMintPreSeed`), establishing an extreme LT-rich hostile ratio.
3. Call `bonding.finalizeGraduation(tokenAddr)` — it does not revert (brick-resistance holds), but the resulting pool price (`_poolPriceLtPerToken`) is asserted to be more than 1.2x the curve-close price (`ltFromPair * 1e18 / tokensForLP`), confirming the LP is seeded materially away from the curve-close price. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** packages/contracts/AGENTS.md (L176-200)
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

### Brick-resistance contract

`_seedUniswapV2Direct` MUST never revert under any pre-seed shape. The brick-resistance contract is the load-bearing security property — it ranks above the LP-capture defense, because a brick locks every holder in `Graduating` forever. The pre-seed defense is layered to honour this:

- **Regime 1/2 don't touch the router.** Even if the V2 router is misbehaving, the empty + donation paths run on direct pair calls.
- **`_pairRebalance` falls back to a direct mint when no swap can run.** `_noFeeSwapInput` may return `s == 0`, or the pair's fee-charging `getAmountOut(s)` may round to zero, against a pre-seed whose swap-output side is dust — `pair.swap` would otherwise revert with `INSUFFICIENT_OUTPUT_AMOUNT`. In either case `_pairRebalance` returns `false`, and `_seedRebalancing` overpowers the dust with a direct `transfer + pair.mint` at the cached `tokensForLP / ltFromPair` ratio (`_seedDirectMint`), opening the pool on-ratio. This is safe specifically because the swap only rounds to zero when the reserves are negligible against this graduation's inventory: the V2 `min()` donation to the attacker's pre-existing LP is then bounded by `max(reserveToken/tokensForLP, reserveLT/ltFromPair)`, which vanishe ... (truncated)
- **`_routerDepositAndDispose` uses `min0=1, min1=1`.** Slippage protection on `addLiquidity` exists to defend against a third party moving the pool ratio between quote and execution; here we set the ratio ourselves in `_pairRebalance` in the same atomic tx, so there's no third party to defend against. The `=1` (rather than `=0`) trips V2's degenerate-ratio guard so the call can't silently land at near-zero.
- **No external dependency on the router slot being correct post-deploy.** `uniswapV2Router` is set at `initialize` time alongside `uniswapV2Factory` and is rejected if zero. There's no live setter — rotation requires a UUPS upgrade so the change is visible on-chain ahead of any in-flight graduation.

Tested end-to-end by the brick-resistance regression tests in `test/TwoPhaseGraduation.t.sol` (notably `test_brick_resistance_frontRun_dust_seed`).
```

**File:** packages/contracts/src/Bonding.sol (L1073-1096)
```text
    function _prepareGraduationLiquidity(
        address tokenAddress
    ) internal returns (uint256 tokensForLP, uint256 ltFromPair, uint256 lpBurned, uint256 unsoldBurned) {
        address pairAddr = _s().tokenInfo[tokenAddress].pair;
        (uint256 tokenReserve, uint256 assetReserve) = IPair(pairAddr).getReserves();

        unsoldBurned = IPair(pairAddr).tokenBalance();
        if (unsoldBurned > 0) {
            Token(tokenAddress).burn(pairAddr, unsoldBurned);
        }

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
